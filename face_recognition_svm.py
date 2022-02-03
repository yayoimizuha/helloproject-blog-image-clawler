# Train multiple images per person
# Find and recognize faces in an image using a SVC with scikit-learn

"""
Structure:
        <test_image>.jpg
        <train_dir>/
            <person_1>/
                <person_1_face-1>.jpg
                <person_1_face-2>.jpg
                .
                .
                <person_1_face-n>.jpg
           <person_2>/
                <person_2_face-1>.jpg
                <person_2_face-2>.jpg
                .
                .
                <person_2_face-n>.jpg
            .
            .
            <person_n>/
                <person_n_face-1>.jpg
                <person_n_face-2>.jpg
                .
                .
                <person_n_face-n>.jpg
"""
import glob
import pprint
import shutil

import face_recognition
import joblib
from sklearn import svm
import os
from tqdm import tqdm
import pandas

# Training the SVC classifier

# The training data would be all the face encodings from all the known images and the labels are their names
encodings = []
names = []

# Training directory
train_dir = os.listdir(os.path.join(os.getcwd(), 'train_dir'))

progress = []
all_files = len(glob.glob('./train_dir/*/*.jpg'))


# def load_image(args):
#     global progress
#     pic_array = args[0]
#     person_name = args[1]
#     encodings
#     for person_img in pic_array:
#         # Get the face encodings for the face in each image file
#         face = face_recognition.load_image_file(os.path.join(os.getcwd(), 'train_dir', person_name, person_img))
#         print("[" + str(len(progress)) + "/" + str(all_files) + "]", end='\t')
#         progress.append(["A"])
#         pprint.pprint(names)
#         print("load: " + os.path.join(os.getcwd(), 'train_dir', person_name, person_img))
#         face_bounding_boxes = face_recognition.face_locations(face)
#
#         # If training image contains exactly one face
#         if len(face_bounding_boxes) == 1:
#             face_enc = face_recognition.face_encodings(face)[0]
#             # Add face encoding for current image with corresponding label (name) to the training data
#             encodings.append(face_enc)
#             names.append(person_name)
#             return [face_enc, person_name]
#         else:
#             print(person_name + "/" + person_img + " was skipped and can't be used for training")
#             return [None, person_name]

def load_image(arg):
    pic = arg
    person_name = str(arg).split('=')[0]

    face = face_recognition.load_image_file(os.path.join(os.getcwd(), 'train_dir', person_name, pic))
    print("[" + str(pix_arr.index(arg)) + "/" + str(all_files) + "]", end='\t')
    print(pic)
    face_bounding_boxes = face_recognition.face_locations(face)
    if len(face_bounding_boxes) == 1:
        face_enc = face_recognition.face_encodings(face)[0]
        # Add face encoding for current image with corresponding label (name) to the training
        return [face_enc, person_name]
    else:
        print(person_name + "/" + pic + " was skipped and can't be used for training")
        return [None, None]


pix_arr = []
# Loop through each person in the training directory
for person in train_dir:
    pix = os.listdir(os.path.join(os.getcwd(), 'train_dir', person))
    pix_arr.extend(pix)
    # pix_arr.append([pix, person])

face_dataset = joblib.Parallel(n_jobs=-1)(joblib.delayed(load_image)(args) for args in pix_arr)

for i in range(len(face_dataset)):
    if face_dataset[i][0] is None and face_dataset[i][1] is None:
        continue
    encodings.append(face_dataset[i][0])
    names.append(face_dataset[i][1])

print(pandas.DataFrame(encodings))
print(pandas.DataFrame(names))
# Loop through each training image for the current person

# Create and train the SVC classifier
clf = svm.SVC(gamma='scale')
clf.fit(encodings, names)

# Load the test image with unknown faces into a numpy array
# test_image = face_recognition.load_image_file(
#     os.path.join(os.getcwd(), 'face_dataset', '佐藤優樹', "佐藤優樹=morningmusume-10ki=12705121595-1-0.jpg"))
#
# # Find all the faces in the test image using the default HOG-based model
# face_locations = face_recognition.face_locations(test_image)
# no = len(face_locations)
# print("Number of faces detected: ", no)
#
# # Predict all the faces in the test image using the trained classifier
# for i in range(no):
#     print("Found:", end='')
#     test_image_enc = face_recognition.face_encodings(test_image)[i]
#     name = clf.predict([test_image_enc])
#     print(*name)

# all_test_data = glob.glob('./face_dataset/*/*.jpg')

all_test_data = []
all_test_data_dirs = os.listdir(os.path.join(os.getcwd(), 'face_dataset'))
for dirs in all_test_data_dirs:
    all_test_data.extend(os.listdir(os.path.join(os.getcwd(), 'face_dataset', dirs)))


# for test_data in all_test_data:
def recognize_face(test_data):
    test_image = face_recognition.load_image_file(
        os.path.join(os.getcwd(), 'face_dataset', test_data.split('=')[0], test_data))
    face_locations = face_recognition.face_locations(test_image)
    no = len(face_locations)
    if no == 0:
        print("No face found in " + test_data)
    print("[" + str(len(all_test_data)) + "/" + str(all_test_data.index(test_data)) + "]\t" + test_data)
    print("Number of faces detected: ", no)

    for faces in range(no):
        print("Found:", end='')
        test_image_enc = face_recognition.face_encodings(test_image)[faces]
        name = clf.predict([test_image_enc])
        print(*name)
        if not os.path.isdir(os.path.join(os.getcwd(), 'recognized_dir', *name)):
            os.mkdir(os.path.join(os.getcwd(), 'recognized_dir', *name))
            print("Create dir: " + str(*name))
        shutil.copy2(os.path.join(os.getcwd(), 'face_dataset', test_data.split('=')[0], test_data),
                     os.path.join(os.getcwd(), 'recognized_dir', *name, test_data))


joblib.Parallel(n_jobs=-1)(joblib.delayed(recognize_face)(test_data) for test_data in all_test_data)
