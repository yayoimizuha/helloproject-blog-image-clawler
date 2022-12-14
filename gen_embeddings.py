import os.path
from PIL import Image
from facenet.src import facenet
import h5py
from glob import glob
import tensorflow as tf
from numpy import array
from tqdm import tqdm

FACE_MODEL_PATH = './20180402-114759/20180402-114759.pb'
HDF5 = h5py.File(name="embeddings.hdf5", mode="a")

print(tf.config.list_physical_devices())
print(tf.config.get_visible_devices())

facenet.load_model(FACE_MODEL_PATH)

input_image_size = 160
sess = tf.compat.v1.Session()
images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
embedding_size = embeddings.get_shape()[1]

fim_path = list()
for dir_path in glob("face_dataset/*"):
    if dir_path == "face_dataset/no_face":
        continue
    fim_path.extend(glob(dir_path + "/*"))


for path in tqdm(fim_path):
    if os.path.basename(path) in HDF5.keys():
        pass
    else:
        image_array = array(Image.open(path).resize((input_image_size, input_image_size),
                                                    Image.Resampling.BILINEAR).convert("RGB"))
        prewhitened = facenet.prewhiten(image_array)
        prewhitened = prewhitened.reshape(-1, prewhitened.shape[0], prewhitened.shape[1], prewhitened.shape[2])
        feed_dict = {images_placeholder: prewhitened, phase_train_placeholder: False}
        HDF5.create_dataset(os.path.basename(path), data=sess.run(embeddings, feed_dict))

HDF5.close()
