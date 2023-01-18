from os import listdir, getcwd, path, makedirs
from random import randint
from shutil import copyfile


dirlist = listdir("dataset")
print(dirlist)
makedirs(path.join(getcwd(), "dataset", "train"), exist_ok=True)
makedirs(path.join(getcwd(), "dataset", "valid"), exist_ok=True)

for idol_name in dirlist:
    for image_name in listdir(path.join(getcwd(), "dataset", idol_name)):
        random_number = randint(0, 9)
        if random_number == 2:
            makedirs(path.join(getcwd(), "dataset", "valid", idol_name), exist_ok=True)
            copyfile(path.join(getcwd(), "dataset", idol_name, image_name),
                     path.join(getcwd(), "dataset", "valid", idol_name, image_name))
        else:
            makedirs(path.join(getcwd(), "dataset", "train", idol_name), exist_ok=True)
            copyfile(path.join(getcwd(), "dataset", idol_name, image_name),
                     path.join(getcwd(), "dataset", "train", idol_name, image_name))
