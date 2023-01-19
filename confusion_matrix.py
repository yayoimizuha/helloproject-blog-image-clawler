from keras.models import load_model, Model
from os import path, getcwd, listdir, makedirs
from keras.preprocessing.image import image_utils
from shutil import copyfile
from numpy import vstack
from pandas import DataFrame
from seaborn import heatmap, set
from matplotlib import pyplot as plt
from japanize_matplotlib import japanize, fonts

variety = "valid"
model: Model = load_model(path.join(getcwd(), "models", "2023-01-19 06:49:13.239003hello.h5"))
acc = loss = 0
images_name = list()
face_dir = listdir(path.join(getcwd(), "dataset", variety))
for directory in face_dir:
    for image in listdir(path.join(getcwd(), "dataset", variety, directory)):
        images_name.append([directory, image])

labels = sorted(face_dir)
confusion_matrix = DataFrame(index=labels, columns=labels, dtype=int)
confusion_matrix.fillna(0, inplace=True)

for directory, image_name in images_name:
    image = image_utils.img_to_array(image_utils.load_img(path.join(
        getcwd(), "dataset", variety, directory, image_name), target_size=(224, 224, 3)))

    ans = model.predict(image[None, ...])
    eve = {key: val for key, val in zip(labels, ans[0])}
    most_proba = sorted(eve.items(), key=lambda acc: acc[1])[-1]
    print(directory, most_proba)
    confusion_matrix.loc[directory, most_proba[0]] += 1
    if directory == most_proba[0]:
        acc += 1
    else:
        loss += 1

japanize()
plt.figure(figsize=(10, 10), dpi=300)
plt.rcParams["font.size"] = 4
heatmap(confusion_matrix, annot=False, square=True, cmap='Blues', xticklabels=1, yticklabels=1, annot_kws={"size": 4})
plt.savefig('confusion_matrix.png')
print(f"acc:{acc},loss:{loss},percent:{acc / (loss + acc)}")
