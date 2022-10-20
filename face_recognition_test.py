import pprint
import cv2
import face_recognition_models
import numpy
from PIL import Image
from face_recognition import load_image_file, face_landmarks, face_locations

image_path = "/home/tomokazu/helloproject-blog-image-clawler/images/高瀬くるみ=beyooooonds-rfro=12524928680-1.jpg"

image = load_image_file(image_path)

face_locs = face_locations(image, model="cnn", number_of_times_to_upsample=1)
face_lms = face_landmarks(image, model="large", face_locations=face_locs)

print(len(face_locs))
pprint.pprint(face_locs)
pprint.pprint(face_lms)

im_rect = numpy.array(Image.open(image_path))
im_rect = cv2.cvtColor(im_rect, cv2.COLOR_RGB2BGR)

for (loc, lm) in zip(face_locs, face_lms):
    top, right, bottom, left = loc
    cv2.rectangle(im_rect, (left, top), (right, bottom), (0, 255, 0))
    for i in lm.keys():
        for j in (lm[i]):
            cv2.circle(im_rect, (j[0], j[1]), 2, (255, 0, 0), -1)

cv2.imshow("image", im_rect)
cv2.waitKey(0)
