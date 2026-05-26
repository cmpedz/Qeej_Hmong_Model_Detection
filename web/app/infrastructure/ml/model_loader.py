import threading

import tensorflow as tf
from tensorflow.keras import layers, regularizers
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam

from app.infrastructure.config.settings import MODEL_PATH


_MODEL = None
_MODEL_LOCK = threading.Lock()

MODEL_REGULARIZATION_CONFIG = {
        "weight_decay": 5e-5,
        "conv_dropout_schedule": [0.2, 0.3],
        "dense_dropout_rate": 0.4,
        "attention_dropout_rate": 0.15,
        "label_smoothing": 0.02,
        "early_stopping_patience": 24,
        "reduce_lr_patience": 8,
}


@tf.keras.utils.register_keras_serializable()
class LearnablePositionalEncoding(layers.Layer):
    def build(self, input_shape):
        sequence_length = input_shape[1]
        feature_dim = input_shape[2]
        if sequence_length is None or feature_dim is None:
            raise ValueError("LearnablePositionalEncoding requires known sequence length and feature dim")
        self.position_embedding = self.add_weight(
            name="position_embedding",
            shape=(sequence_length, feature_dim),
            initializer="zeros",
            trainable=True,
        )

    def call(self, inputs):
        return inputs + self.position_embedding

    def get_config(self):
        return super().get_config()
    
def transformer_block(x, num_heads=4, dropout_rate=0.2, l2_strength=1e-4):

    d_model = x.shape[-1]
    l2_reg = regularizers.l2(l2_strength)

    ff_dim = 4 * d_model
    key_dim = max(1, d_model // num_heads)

    print("check d_model", d_model)
    print("check ff_dim", ff_dim)

    attn_output = layers.MultiHeadAttention(
        num_heads=num_heads,
        key_dim=key_dim,
        output_shape=d_model,
        dropout=dropout_rate
    )(x, x)
    attn_output = layers.Dropout(dropout_rate)(attn_output)

    x = layers.Add()([x, attn_output])
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    print("check x shape after attention block", x.shape)

    ffn_output = layers.Dense(ff_dim, activation="relu", kernel_regularizer=l2_reg)(x)
    print("check ffn shape after Dense 1", ffn_output.shape)
    ffn_output = layers.Dropout(dropout_rate)(ffn_output)
    ffn_output = layers.Dense(d_model, kernel_regularizer=l2_reg)(ffn_output)
    print("check ffn shape after Dense 2", ffn_output.shape)
    ffn_output = layers.Dropout(dropout_rate)(ffn_output)

    x = layers.Add()([x, ffn_output])
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    print("check x shape after feed-forward block", x.shape)

    return x

def conv_block(x, filters, pool_size = (2, 2), dropout_rate = 0.25, l2_strength = 1e-4):
    l2_reg = regularizers.l2(l2_strength)

    x = layers.Conv2D(filters, (3,3), padding="same", kernel_regularizer=l2_reg)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.MaxPooling2D(pool_size=pool_size, strides=2)(x)
    x = layers.SpatialDropout2D(dropout_rate)(x)
    return x

def get_features_after_model_pipeline(model_input):

    reg_config = MODEL_REGULARIZATION_CONFIG
    weight_decay = reg_config["weight_decay"]
    attention_dropout_rate = reg_config["attention_dropout_rate"]
    dense_dropout_rate = reg_config["dense_dropout_rate"]
    conv_dropout_schedule = reg_config["conv_dropout_schedule"]

    x = conv_block(model_input, 32, pool_size=(2, 2), dropout_rate=conv_dropout_schedule[0], l2_strength=weight_decay)
    print("check x shape after MP 1", x.shape)

    x = conv_block(x, 64, pool_size=(2, 2), dropout_rate=conv_dropout_schedule[1], l2_strength=weight_decay)
    print("check x shape after MP 2", x.shape)

    x = layers.Permute((2, 1, 3))(x)
    print("check x shape after permute to time-major", x.shape)

    time_steps = x.shape[1]
    feature_dim = x.shape[2] * x.shape[3]
    x = layers.Reshape((time_steps, feature_dim))(x)
    print("check x shape after reshape for transformer", x.shape)

    x = layers.Dense(64, kernel_regularizer=regularizers.l2(weight_decay))(x)
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    x = layers.Dropout(attention_dropout_rate)(x)

    # Add positional information before the Transformer stack.
    x = LearnablePositionalEncoding()(x)
    print("check x shape after positional encoding", x.shape)

    # Transformer encoder stack: 3 layers.
    t1 = transformer_block(x, dropout_rate=attention_dropout_rate, l2_strength=weight_decay)
    t2 = transformer_block(t1, dropout_rate=attention_dropout_rate, l2_strength=weight_decay)
    t3 = transformer_block(t2, dropout_rate=attention_dropout_rate, l2_strength=weight_decay)

    #concatenate
    x = layers.Concatenate()([t1, t2, t3])
    print("check x shape after concatenate layer", x.shape)

    #fully connected
    x = layers.Dense(128, activation="relu", kernel_regularizer=regularizers.l2(weight_decay))(x)
    print("check x shape after fully connected layer 1", x.shape)
    x = layers.Dropout(dense_dropout_rate)(x)

    x = layers.Dense(64, activation="relu", kernel_regularizer=regularizers.l2(weight_decay))(x)
    print("check x shape after fully connected layer 2", x.shape)

    x = layers.Dropout(dense_dropout_rate)(x)

    x = layers.GlobalAveragePooling1D()(x)

    print("check x shape after GlobalAveragePooling1D", x.shape)

    return x



def build_cv_model(input_shape=(168, 9, 1), num_classes=7, learning_rate= 0.0001):

    reg_config = MODEL_REGULARIZATION_CONFIG
    weight_decay = reg_config["weight_decay"]
    label_smoothing = reg_config["label_smoothing"]

    model_input = layers.Input(shape=input_shape)

    x = get_features_after_model_pipeline(model_input)
    x = layers.Activation("linear", name="train_embedding")(x)

    model_output = layers.Dense(num_classes, activation="sigmoid", kernel_regularizer=regularizers.l2(weight_decay))(x)

    model = tf.keras.Model(model_input, model_output)
    model_optimizer = Adam(learning_rate=learning_rate, clipnorm=1.0)
    model.compile(
        optimizer=model_optimizer,
        loss=tf.keras.losses.BinaryCrossentropy(label_smoothing=label_smoothing),
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="binary_accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="pr_auc", curve="PR", multi_label=True, num_labels=num_classes)
        ]
    )
    return model




def get_model():
    global _MODEL
    with _MODEL_LOCK:
        if _MODEL is None:
            if not MODEL_PATH.is_file():
                raise FileNotFoundError(f"Cannot find model file at {MODEL_PATH}")
            _MODEL = build_cv_model()
            _MODEL.load_weights(MODEL_PATH)
    return _MODEL
