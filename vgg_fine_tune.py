from keras.layers import Dense, Input, GlobalAveragePooling2D, Dropout, Flatten, Activation
from keras.optimizers import Adam, SGD
from keras.activations import relu, sigmoid, softmax
# from keras.applications.vgg16 import VGG16, preprocess_input
# from keras.applications.vgg19 import VGG19, preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import TensorBoard
from keras.models import Model
from os import getcwd, path
from keras_vggface.utils import preprocess_input
from keras_vggface import VGGFace
from datetime import datetime

TRAIN_PATH = path.join(getcwd(), "dataset", "train")
VALID_PATH = path.join(getcwd(), "dataset", "valid")

NOW = datetime.now()

num_classes = 99
batch_size = 16
epochs = 50
hidden_dim = 512

train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input,
                                   rotation_range=20,
                                   horizontal_flip=True,
                                   height_shift_range=0.2,
                                   width_shift_range=0.2,
                                   zoom_range=0.2,
                                   brightness_range=[0.7, 1.0])
train_generator = train_datagen.flow_from_directory(
    TRAIN_PATH,
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=False
)

valid_datagen = ImageDataGenerator(preprocessing_function=preprocess_input,
                                   rotation_range=20,
                                   horizontal_flip=True,
                                   height_shift_range=0.2,
                                   width_shift_range=0.2,
                                   zoom_range=0.2,
                                   brightness_range=[0.7, 1.0])
valid_generator = valid_datagen.flow_from_directory(
    VALID_PATH,
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=False
)

print(train_generator.class_indices)
print(valid_generator.class_indices)
input_tensor = Input(shape=(224, 224, 3))
vgg16_model = VGGFace(
    include_top=False,
    #   weights='imagenet',
    input_tensor=input_tensor
)

for layer in vgg16_model.layers[:17]:
    layer.trainable = False

# x = vgg16_model.output
# x = GlobalAveragePooling2D()(x)
# x = Dense(hidden_dim, activation='relu', name='fc6')(x)
# # x = Dense(hidden_dim, activation='relu', name='fc7')(x)
# x = Dropout(0.5)(x)
# predictions = Dense(num_classes, activation='softmax', name='classifier')(x)
last_layer = vgg16_model.get_layer('pool5').output
x = Flatten(name='flatten')(last_layer)
x = Dense(hidden_dim, activation=relu, name='fc6')(x)
x = Dense(hidden_dim, activation=relu, name='fc7')(x)
predictions = Dense(num_classes, activation=softmax, name='fc8')(x)

model = Model(inputs=vgg16_model.inputs, outputs=predictions)
tb_cb = TensorBoard(log_dir=path.join(getcwd(), "tf_log", NOW.__str__()), histogram_freq=1)

optimizer = Adam(learning_rate=0.0001)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

model.summary()

for i in model.layers:
    print(i.name, i.trainable)

history = model.fit(
    train_generator,
    validation_data=valid_generator,
    epochs=epochs,
    batch_size=batch_size,
    callbacks=[tb_cb]
)

model.save(path.join(getcwd(), "models", NOW.__str__() + "hello.h5"))
