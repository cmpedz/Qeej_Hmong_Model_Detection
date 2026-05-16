import threading

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import load_model

from app.infrastructure.config.settings import MODEL_PATH


_MODEL = None
_MODEL_LOCK = threading.Lock()


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


def get_model():
    global _MODEL
    with _MODEL_LOCK:
        if _MODEL is None:
            if not MODEL_PATH.is_file():
                raise FileNotFoundError(f"Cannot find model file at {MODEL_PATH}")
            _MODEL = load_model(MODEL_PATH)
    return _MODEL
