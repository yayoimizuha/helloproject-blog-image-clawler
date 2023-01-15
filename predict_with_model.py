from keras.models import load_model, Model
from os import path, getcwd, listdir, makedirs
from keras.preprocessing.image import image_utils
from shutil import copyfile
from numpy import vstack

model: Model = load_model(path.join(getcwd(), "models", "2023-01-15 12:13:58.165751hello.h5"))
model.summary()

images_name = list()
face_dir = listdir(path.join(getcwd(), "face_dataset"))
for directory in face_dir:
    for image in listdir(path.join(getcwd(), "face_dataset", directory)):
        images_name.append([directory, image])

labels = sorted(listdir(path.join(getcwd(), "dataset", "train")))
print(labels)
for label in labels:
    makedirs(path.join(getcwd(), "predicted", label), exist_ok=True)

for directory, image_name in images_name:
    try:
        image = image_utils.img_to_array(image_utils.load_img(path.join(getcwd(), "face_dataset", directory, image_name)
                                                              , target_size=(224, 224, 3)))
    except:
        continue
    ans = model.predict(image[None, ...])
    eve = {key: val for key, val in zip(labels, ans[0])}
    most_proba = sorted(eve.items(), key=lambda acc: acc[1])[-1]
    print(most_proba)
    if most_proba[1] < 0.8:
        continue
    copyfile(path.join(getcwd(), "face_dataset", directory, image_name),
             path.join(getcwd(), "predicted", most_proba[0], image_name))
