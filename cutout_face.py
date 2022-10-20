import time
from pathlib import Path
from PIL import Image, ImageFile
import os
import joblib
import pprint
import mediapipe_recognition_test

now_time = time.time()
# if dlib.DLIB_USE_CUDA:
#     face_recognition_option = 'batch_size=128'
# else:
#     face_recognition_option = ""
N_JOBS = 8

exist_image_file = [f for f in sorted(os.listdir(os.path.join(os.getcwd(), 'images')), reverse=True) if
                    os.path.isfile(os.path.join(os.getcwd(), 'images', f))]
exist_image_file = [f for f in exist_image_file if '.jpg' in f]

exist_dataset_file = []
exist_dataset_dir = []

for dir_dataset in os.listdir(os.path.join(os.getcwd(), 'face_dataset')):
    if not os.path.isdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)):
        continue
    exist_dataset_dir.append(dir_dataset)
    for file in os.listdir(os.path.join(os.getcwd(), 'face_dataset', dir_dataset)):
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
pprint.pprint(sorted(set(tags) - set(exist_dataset_dir)))

for tag in tags:
    if not os.path.exists(os.path.join(os.getcwd(), 'face_dataset',
                                       str(os.path.splitext(os.path.basename(tag))[0]).split('=')[0])):
        print("mkdir: " + tag)
        os.mkdir(os.path.join(os.getcwd(), 'face_dataset',
                              str(os.path.splitext(os.path.basename(tag))[0]).split('=')[0]))


def cut_out_face(image_path):
    face_array = mediapipe_recognition_test.mediapipe_face_detect(image_path)
    print(len(face_array))
    print(image_path)
    image_order = 0
    last_write_time = os.stat(path=image_path).st_mtime
    if not face_array:
        return

    filename_no_face = ""

    for face_image in face_array:
        filename = os.path.join(os.getcwd(), 'face_dataset',
                                str(os.path.splitext(os.path.basename(image_path))[0]).split('=')[0],
                                str(os.path.splitext(os.path.basename(image_path))[0]) + '-' +
                                str(image_order) + '.jpg')
        filename_no_face = os.path.join(os.getcwd(), 'face_dataset', 'no_face',
                                        str(os.path.splitext(os.path.basename(image_path))[0]) + '-' +
                                        str(image_order) + '.jpg')

        # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom,
        #                                                                                             right))

        pil_image = Image.fromarray(face_image, mode="RGB")
        pil_image.save(filename)
        os.utime(path=filename, times=(last_write_time, last_write_time))

        image_order += 1
    print("")
    if image_order == 0:
        Path(filename_no_face).touch()


joblib.Parallel(n_jobs=N_JOBS)(joblib.delayed(cut_out_face)(image_path) for image_path in images)

print(str(time.time() - now_time) + " sec")
