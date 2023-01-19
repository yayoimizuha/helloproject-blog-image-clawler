from keras.models import load_model, Model
from os import path, getcwd, listdir, makedirs
from keras.preprocessing.image import image_utils
from shutil import copyfile
from numpy import argmax, stack
from tensorflow import math

model: Model = load_model(path.join(getcwd(), "models", "2023-01-15.12.13.58.165751.h5"))
model.summary()

images_name = list()
face_dir = listdir(path.join(getcwd(), "face_dataset"))
for directory in face_dir:
    if directory == "no_face":
        continue
    for image in listdir(path.join(getcwd(), "face_dataset", directory)):
        images_name.append([directory, image])

labels = sorted(listdir(path.join(getcwd(), "dataset", "train")))
print(labels)
for label in labels:
    makedirs(path.join(getcwd(), "predicted", label), exist_ok=True)

chunk = 300
ans_l = list()
images_path = list()
for order in range(0, images_name.__len__(), chunk):
    print(order, images_name.__len__(), sep="/")
    images_name_chunk = images_name[order: order + chunk]
    images = list()
    for directory, image_name in images_name_chunk:
        try:
            images.append(image_utils.img_to_array(image_utils.load_img(
                path.join(getcwd(), "face_dataset", directory, image_name), target_size=(224, 224, 3))))
            images_path.append(path.join(getcwd(), "face_dataset", directory, image_name))
        except:
            print("error")
            pass
            # continue
    if not images:
        continue
    # answers = model.predict(stack(images))
    answers = model(stack(images), training=False)
    # ans_l.extend(argmax(answers.numpy(), axis=1).tolist())
    ans_l.extend(math.argmax(answers, axis=1).numpy().tolist())

for image_path, answer in zip(images_path, ans_l):
    copyfile(image_path, path.join(getcwd(), "predicted", labels[answer], path.basename(image_path)))
