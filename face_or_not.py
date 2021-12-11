import face_recognition
from PIL import Image
import os
import joblib
import pprint
import time

N_JOBS = 6

exist_image_file = [f for f in sorted(os.listdir(os.path.join(os.getcwd(), 'images')), reverse=True) if
                    os.path.isfile(os.path.join(os.getcwd(), 'images', f))]
exist_image_file = [f for f in exist_image_file if '.jpg' in f]

exist_file = []
for dirPath, dirs, files in os.walk(os.path.join(os.getcwd(), 'face_dataset')):
    if not files:
        continue
    pprint.pprint(files)
    exist_file.extend(files)
pprint.pprint(exist_file)
exist_file = "".join(exist_file)

# time.sleep(50)

# exist_image_file = ["ブログ=angerme-amerika=11980474019-1.jpg"]

images = []
for f in exist_image_file:
    images.append(os.path.join(os.getcwd(), 'images', f))

tags = []
for f in exist_image_file:
    tags.append(f.split('=')[0])
tags = list(sorted(set(tags)))
pprint.pprint(sorted(tags))
for tag in tags:
    if not os.path.exists(os.path.join(os.getcwd(), 'face_dataset',
                                       str(os.path.splitext(os.path.basename(tag))[0]).split('=')[0])):
        print("mkdir: " + tag)
        os.mkdir(os.path.join(os.getcwd(), 'face_dataset',
                              str(os.path.splitext(os.path.basename(tag))[0]).split('=')[0]))


def cut_out_face(image_path):
    print("Image Path: " + os.path.basename(image_path))
    if os.path.basename(image_path)[:-4] in exist_file:
        print("This file is already proceed. :" + os.path.basename(image_path) + "\n\n\n")
        return 0

    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    print("\n\n\n" + str(face_locations))
    print(image.shape)
    print(image_path)
    image_order = 0
    last_write_time = os.stat(path=image_path).st_atime
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

        # 画像サイズが0なら返す
        if (top - bottom) * (right - left) == 0:
            continue
        # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom,
        #                                                                                             right))

        face_image = image[top:bottom, left:right]
        print(str(top) + ',' + str(bottom) + ',' + str(left) + ',' + str(right))
        pil_image = Image.fromarray(face_image)

        filename = os.path.join(os.getcwd(), 'face_dataset',
                                str(os.path.splitext(os.path.basename(image_path))[0]).split('=')[0],
                                str(os.path.splitext(os.path.basename(image_path))[0]) + '-' +
                                str(image_order) + '.jpg')
        pil_image.save(filename)
        os.utime(path=filename, times=(last_write_time, last_write_time))

        image_order += 1


joblib.Parallel(n_jobs=N_JOBS)(joblib.delayed(cut_out_face)(image_path) for image_path in images)
