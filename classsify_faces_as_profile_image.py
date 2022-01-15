import os
import pickle
import random
import sys
import time
import face_recognition
import joblib
import matplotlib.pyplot as plt
import pprint
from PIL import Image, ImageDraw, ImageFont
import numpy as np

N_JOBS = 6

member_pics = os.listdir('member_infographics')
member_pics.remove('get-ufg-pic.py')
member_pics.remove('在籍者なし.jpg')
pprint.pprint(member_pics)

known_face_encodings = []
known_face_names = []

# process_file = [f for f in os.listdir(os.path.join(os.getcwd(), 'images')) if
#               os.path.isfile(os.path.join(os.getcwd(), 'images', f))]

process_file = []
for pics in os.listdir(os.path.join(os.getcwd(), 'images')):
    # print(os.stat(path=os.path.join(os.getcwd(), 'images', pics)).st_mtime)
    # print(time.time() - 60 * 60 * 24 * 31 * 3)
    if os.stat(path=os.path.join(os.getcwd(), 'images', pics)).st_mtime > time.time() - 60 * 60 * 24 * 31 * 3:
        print('add: ' + pics)
        process_file.append(pics)

# only image file
process_file = [f for f in process_file if '.jpg' in f]
random.shuffle(process_file)

process_file = list(set(process_file) - set(os.listdir(os.path.join(os.getcwd(), 'drawn_box'))))

with open('face_encoding.bin', 'rb') as f:
    known_face_encodings = pickle.load(f)

for files in member_pics:
    known_face_encodings.append(face_recognition.face_encodings(
        face_recognition.load_image_file(os.path.join(os.getcwd(), 'member_infographics', files)))[0])
    print(files.split('.')[0])
    known_face_names.append(files.split('.')[0])

with open('face_encoding.bin', 'wb') as f:
    pickle.dump(known_face_encodings, f)


# for unknown_image in process_file:
def draw_box_on_face(unknown_image):
    if '.jpg' not in unknown_image:
        return 0
    # time.sleep(3)
    print(unknown_image)
    filename = unknown_image
    unknown_image = face_recognition.load_image_file(os.path.join(os.getcwd(), 'images', unknown_image))
    try:
        face_locations = face_recognition.face_locations(unknown_image)
        # face_locations = face_recognition.face_locations(unknown_image, model='cnn')
    except BaseException as error:
        print(error)
        return 0
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
    pil_image = Image.fromarray(unknown_image)
    draw = ImageDraw.Draw(pil_image)
    if not face_locations:
        return 0
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = 'Unknown'
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            font = ImageFont.truetype("C:\\Windows\\Fonts\\BIZ-UDMinchoM.ttc")
            text_width, text_height = draw.textsize(name, font=font)
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255), font=font)

    del draw
    pil_image.save(fp=os.path.join(os.getcwd(), 'drawn_box', filename))
    # pil_image.show()
    # plt.imshow(pil_image)
    # plt.show()


sys.exit()
joblib.Parallel(n_jobs=N_JOBS)(joblib.delayed(draw_box_on_face)(image_path) for image_path in process_file)
