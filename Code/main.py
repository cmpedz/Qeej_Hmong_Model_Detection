
import numpy as np
from module.DataModule import DataModule
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D
from tensorflow.keras.layers import Dense, Dropout, Flatten
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from sklearn.utils.class_weight import compute_class_weight

#label data
audio_dir = "../Data/audio/Khèn 1/Đơn_ống"
labels_dir = "../Data/labels/Khèn 1/Đơn_ống"
dataModule = DataModule()
X, y = dataModule.build_dataset(audio_dir, labels_dir)

#label encoding
le = LabelEncoder()
y_int = le.fit_transform(y)
y_cat = to_categorical(y_int)

class_names = le.classes_


#set up model
model = Sequential([
    Conv1D(32, kernel_size=5, activation='relu',
           input_shape=(X.shape[1], 1)),
    MaxPooling1D(2),
    Dropout(0.25),

    Conv1D(64, kernel_size=5, activation='relu'),
    MaxPooling1D(2),
    Dropout(0.25),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),

    Dense(y_cat.shape[1], activation='softmax')
])

model.compile(
    optimizer='adadelta',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

#trainning model

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y_cat, test_size=0.1, stratify=y_int)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5)

y_train_int = np.argmax(y_train, axis=1)
print("check y train int:", y_train_int)

class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(y_train_int),
    y=y_train_int
)

class_weight_dict = dict(enumerate(class_weights))

print("check class weight dict:", class_weight_dict)

model.fit(
    X_train[..., np.newaxis],
    y_train,
    validation_data=(X_val[..., np.newaxis], y_val),
    class_weight=class_weight_dict,
    epochs=30,
    batch_size=100
)

#assess model
y_pred = model.predict(X_test[..., np.newaxis])
y_pred = np.argmax(y_pred, axis=1)
y_true = np.argmax(y_test, axis=1)

print("check y pred:", y_pred)
print("check y true:", y_true)

#F1 score, ...
print(classification_report(
    y_true, y_pred,
    target_names=class_names
))

#confuse matrix
cm = confusion_matrix(y_true, y_pred)

fig, ax = plt.subplots(figsize=(18, 16))
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=class_names  
)
disp.plot(ax=ax)

plt.xlabel("Predicted label")
plt.ylabel("True label")
plt.title("Confusion Matrix (10 ms windows)")
plt.show()