import shutil
import os

for dir_dataset in os.listdir(os.path.join(os.getcwd(), 'face_dataset')):

    if not os.path.isdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)):
        continue

    if not os.path.isdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset, 'train')):
        os.mkdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset, 'train'))
        print("Create dir: " + dir_dataset)

    print(len(os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset))))

    for file in os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)) \
            [::int((len(os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)))) / 40) + 1]:

        if '.jpg' not in file:
            continue

        print(dir_dataset, file)

        shutil.copy2(os.path.join(os.getcwd(), 'face_dataset', dir_dataset, file),
                     os.path.join(os.getcwd(), 'face_dataset', dir_dataset, 'train', file))
