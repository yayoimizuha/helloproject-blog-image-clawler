import os
import shutil

from facenet.src import facenet
import tensorflow as tf
import numpy as np
from PIL import Image
import glob
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib


def load_image(image_path, width, height, mode):
    image = Image.open(image_path)
    image = image.resize((width, height), Image.BILINEAR)
    return np.array(image.convert(mode))


print(tf.version.VERSION)


class FaceEmbedding(object):

    def __init__(self, model_path):
        # モデルを読み込んでグラフに展開
        facenet.load_model(model_path)

        self.input_image_size = 160
        self.sess = tf.Session()
        self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        self.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        self.embedding_size = self.embeddings.get_shape()[1]

    def __del__(self):
        self.sess.close()

    def face_embeddings(self, image_path):
        image = load_image(image_path, self.input_image_size, self.input_image_size, 'RGB')
        prewhitened = facenet.prewhiten(image)
        prewhitened = prewhitened.reshape(-1, prewhitened.shape[0], prewhitened.shape[1], prewhitened.shape[2])
        feed_dict = {self.images_placeholder: prewhitened, self.phase_train_placeholder: False}
        embeddings = self.sess.run(self.embeddings, feed_dict=feed_dict)
        return embeddings


FACE_MODEL_PATH = './20180402-114759/20180402-114759.pb'
face_embedding = FaceEmbedding(FACE_MODEL_PATH)

fim_path = glob.glob("/home/tomokazu/helloproject-blog-image-clawler/face_dataset/橋迫鈴/*.jpg")

# 顔画像から特徴ベクトルを抽出
features = np.array([face_embedding.face_embeddings(f)[0] for f in fim_path])
print(features.shape)

# pca = PCA(n_components=6)
# pca.fit(features)
# reduced = pca.fit_transform(features)
# print(reduced.shape)

tsne = TSNE(n_components=3)
tsne.fit(features)
reduced = tsne.fit_transform(features)
print(reduced.shape)

K = 13
kmeans = KMeans(n_clusters=K).fit(reduced)
pred_label = kmeans.predict(reduced)
x = reduced[:, 0]
y = reduced[:, 1]

# dbscan = DBSCAN(eps=25, min_samples=100).fit(reduced)
# pred_label = dbscan.labels_

plt.scatter(x, y, c=pred_label)
plt.colorbar()
plt.savefig("graph1.png")
print(fim_path)
print(pred_label)
shutil.rmtree("clustered")
os.mkdir("clustered")
for i in range(0, K):
    os.makedirs(os.path.join(os.getcwd(), "clustered", str(i)), exist_ok=True)
for file_path, cluster in zip(fim_path, pred_label):
    os.symlink(file_path, os.path.join(os.getcwd(), "clustered", str(cluster), os.path.basename(file_path)))


def imscatter(x, y, image_path, ax=None, zoom=1):
    if ax is None:
        ax = plt.gca()

    artists = []
    for x0, y0, image in zip(x, y, image_path):
        image = plt.imread(image)
        im = OffsetImage(image, zoom=zoom)
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    return artists


x = reduced[:, 0]
y = reduced[:, 1]
fig, ax = plt.subplots(figsize=(40, 40))
imscatter(x, y, fim_path, ax=ax, zoom=.2)
ax.plot(x, y, 'ko', alpha=0)
ax.autoscale()
plt.savefig("graph2.png")
