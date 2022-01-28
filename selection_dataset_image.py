import shutil
import os

for dir_dataset in os.listdir(os.path.join(os.getcwd(), 'face_dataset')):

    if not os.path.isdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)):
        continue

    if not os.path.isdir(os.path.join(os.getcwd(), 'face_dataset-2021-12-27', dir_dataset)):
        os.mkdir(os.path.join(os.getcwd(), 'face_dataset-2021-12-27', dir_dataset))
        print("Create dir: " + dir_dataset)

    print(len(os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset))))

    for file in os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)) \
            [::int((len(os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)))) / 30) + 1]:

        if '.jpg' not in file:
            continue

        print(dir_dataset, file)

        shutil.copy2(os.path.join(os.getcwd(), 'face_dataset', dir_dataset, file),
                     os.path.join(os.getcwd(), 'face_dataset-2021-12-27', dir_dataset, file))
