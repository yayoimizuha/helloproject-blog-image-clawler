import os
import face_recognition
import glob
import pprint
from PIL import Image, ImageDraw
import numpy as np

member_pics = os.listdir('member_infographics')
member_pics.remove('get-ufg-pic.py')
member_pics.remove('在籍者なし.jpg')
pprint.pprint(member_pics)

known_face_encodings = []
known_face_names = []

exist_file = [f for f in os.listdir(os.path.join(os.getcwd(), 'images')) if
              os.path.isfile(os.path.join(os.getcwd(), 'images', f))]
# only image file
exist_file = [f for f in exist_file if '.jpg' in f]

for files in member_pics:
    known_face_encodings.append(face_recognition.face_encodings(
        face_recognition.load_image_file(os.path.join(os.getcwd(), 'member_infographics', files)))[0])
    print(files.split('.')[0])
    known_face_names.append(files.split('.')[0])

for unknown_image in os.listdir(os.path.join(os.getcwd(), 'images')):
    try:
        face_locations = face_recognition.face_locations(unknown_image)
    except BaseException as error:
        print(error)
        continue
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
    pil_image = Image.fromarray(unknown_image)
    draw = ImageDraw.Draw(pil_image)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = 'Unknown'
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    del draw
    pil_image.show()
