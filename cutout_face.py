import time
import face_recognition
from pathlib import Path
from PIL import Image
import os
import joblib
import pprint
import dlib
from colorama import Fore, Back, Style

now_time = time.time()
print("Is Dlib Using CUDA?: " + str(dlib.DLIB_USE_CUDA))
# if dlib.DLIB_USE_CUDA:
#     face_recognition_option = 'batch_size=128'
# else:
#     face_recognition_option = ""
N_JOBS = 8

exist_image_file = [f for f in sorted(os.listdir(os.path.join(os.getcwd(), 'images')), reverse=True) if
                    os.path.isfile(os.path.join(os.getcwd(), 'images', f))]
exist_image_file = [f for f in exist_image_file if '.jpg' in f]

exist_dataset_file = []

for dir_dataset in os.listdir(os.path.join(os.getcwd(), 'face_dataset')):
    if not os.path.isdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset, 'train')):
        continue
    for file in os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset, 'train')):
        if '.jpg' not in file:
            continue
        exist_dataset_file.append(file.rsplit('-', 1)[0] + '.jpg')
exist_dataset_file = list(set(exist_dataset_file))
# print(Fore.BLUE)
# pprint.pprint(exist_dataset_file)
# print(Fore.RESET)
# time.sleep(3)
# print(Fore.GREEN)
# pprint.pprint(exist_image_file)
# print(Fore.RESET)
print([len(exist_dataset_file), len(exist_image_file)])
images = []
for f in set(exist_image_file) - set(exist_dataset_file):
    images.append(os.path.join(os.getcwd(), 'images', f))

print("Begin Processing: " + str(len(images)))

# Creating Directory.
tags = []
for f in exist_image_file:
    tags.append(f.split('=')[0])
tags = list(sorted(set(tags)))
tags.append('no_face')
pprint.pprint(sorted(tags))

for tag in tags:
    if not os.path.exists(os.path.join(os.getcwd(), 'face_dataset',
                                       str(os.path.splitext(os.path.basename(tag))[0]).split('=')[0])):
        print("mkdir: " + tag)
        os.mkdir(os.path.join(os.getcwd(), 'face_dataset',
                              str(os.path.splitext(os.path.basename(tag))[0]).split('=')[0]))


def cut_out_face(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    print(str(face_locations))
    print(image.shape)
    print(image_path)
    image_order = 0
    last_write_time = os.stat(path=image_path).st_mtime
    if not face_locations:
        face_locations = [(10, 10, 10, 10)]

    filename_no_face = ""

    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        top -= int((bottom - top) * 0.6)
        if top < 0:
            top = 0
        bottom += int((bottom - top) * 0.2)
        if bottom > int(image.shape[0]) - 1:
            bottom = image.shape[0] - 1
        left -= int((right - left) * 0.2)
        if left < 0:
            left = 0
        right += int((right - left) * 0.2)
        if right > int(image.shape[1]) - 1:
            right = image.shape[1] - 1

        filename = os.path.join(os.getcwd(), 'face_dataset',
                                str(os.path.splitext(os.path.basename(image_path))[0]).split('=')[0],
                                str(os.path.splitext(os.path.basename(image_path))[0]) + '-' +
                                str(image_order) + '.jpg')
        filename_no_face = os.path.join(os.getcwd(), 'face_dataset', 'no_face',
                                        str(os.path.splitext(os.path.basename(image_path))[0]) + '-' +
                                        str(image_order) + '.jpg')
        # 画像サイズが0なら返す
        if (top - bottom) * (right - left) == 0:
            print("Image is blank")
            continue
        if (bottom - top) < 150 or (right - left) < 150:
            print("Image is too small")
            continue

        # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom,
        #                                                                                             right))

        face_image = image[top:bottom, left:right]
        print(str(top) + ',' + str(bottom) + ',' + str(left) + ',' + str(right))
        pil_image = Image.fromarray(face_image)

        pil_image.save(filename)
        os.utime(path=filename, times=(last_write_time, last_write_time))

        image_order += 1
    print("")
    if image_order == 0:
        Path(filename_no_face).touch()


joblib.Parallel(n_jobs=N_JOBS)(joblib.delayed(cut_out_face)(image_path) for image_path in images)

print(str(time.time() - now_time) + " sec")
