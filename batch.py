import glob
import os
import os
import pprint
import shutil
import time

from facenet.src import facenet
import numpy as np
from PIL import Image
import glob
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
# from tsnecuda import TSNE
from sklearn.cluster import KMeans, DBSCAN
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib
import multiprocessing
from umap import UMAP
from scipy.cluster.hierarchy import linkage, fcluster


# import gpumap

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def load_image(image_path, width, height, mode):
    image = Image.open(image_path)
    image = image.resize((width, height), Image.Resampling.BILINEAR)
    return np.array(image.convert(mode))


FACE_MODEL_PATH = './20180402-114759/20180402-114759.pb'

pprint.pprint(glob.glob("/home/tomokazu/helloproject-blog-image-clawler/face_dataset/*"))

shutil.rmtree("clustered")
os.mkdir("clustered")


def face_emb(path, dummy, ret_list):
    # return [face_embedding.face_embeddings(f)[0] for f in fim_path]

    import tensorflow as tf
    tf.config.threading.set_intra_op_parallelism_threads(1)

    # print(tf.version.VERSION)

    class FaceEmbedding(object):

        def __init__(self, model_path):
            # モデルを読み込んでグラフに展開
            facenet.load_model(model_path)

            self.input_image_size = 160
            self.sess = tf.compat.v1.Session()
            self.images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
            self.embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
            self.phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
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

    face_embedding = FaceEmbedding(FACE_MODEL_PATH)

    for p in path:
        ret_list.append(face_embedding.face_embeddings(p)[0])


for dir_path in glob.glob("/home/tomokazu/helloproject-blog-image-clawler/face_dataset/*"):

    if dir_path == "/home/tomokazu/helloproject-blog-image-clawler/face_dataset/no_face":
        continue
    fim_path = glob.glob(dir_path + "/*")
    person_name = os.path.basename(dir_path)
    os.mkdir(os.path.join(os.getcwd(), "clustered", person_name))

    print(person_name)

    # 顔画像から特徴ベクトルを抽出
    emb_time = time.time()
    manager = multiprocessing.Manager()
    dummy_dict = manager.dict()
    return_list = manager.list()
    process = multiprocessing.Process(target=face_emb, args=(fim_path, dummy_dict, return_list))
    process.start()
    process.join()
    print("FaceNet Time: " + str(time.time() - emb_time))

    features = np.array(return_list)
    process.close()

    print(features.shape)

    dim_reduction_time = time.time()
    # pca_time = time.time()
    reduced = PCA(n_components=70).fit_transform(features)
    # print("PCA Dimensionality reduction Time: " + str(time.time() - pca_time))
    # umap_time = time.time()
    # reduced = UMAP(n_components=30).fit_transform(reduced)
    # reduced = PCA(n_components=7).fit_transform(reduced)
    reduced = UMAP(n_components=7).fit_transform(reduced)
    # print("UMAP Dimensionality reduction Time: " + str(time.time() - umap_time))
    print(reduced.shape)

    # tsne = TSNE(n_components=3, learning_rate='auto', init='pca')
    # tsne.fit(features)
    # reduced = tsne.fit_transform(features)
    # print(reduced.shape)
    print("Dimensionality reduction Time: " + str(time.time() - dim_reduction_time))

    kmeans_time = time.time()
    K = 13
    kmeans = KMeans(n_clusters=K).fit(reduced)
    pred_label = kmeans.predict(reduced)
    # pred_label = fcluster(linkage(reduced, method='ward'), t=K - 1, criterion="maxclust")
    x = reduced[:, 0]
    y = reduced[:, 1]
    print("K-means Time: " + str(time.time() - kmeans_time))
    # plt.figure(figsize=(50, 50))
    # plt.scatter(x, y, c=DBSCAN(min_samples=20, eps=.7).fit(reduced).labels_, cmap='tab10')
    # plt.colorbar()
    # plt.savefig(os.path.join(os.getcwd(), "clustered", person_name, "dbscan.png"))

    image_output_time = time.time()
    # dbscan = DBSCAN(eps=25, min_samples=100).fit(reduced)
    # pred_label = dbscan.labels_
    plt.figure(figsize=(50, 50))

    plt.scatter(x, y, c=pred_label.astype(int), s=300, cmap='tab10')
    plt.colorbar()
    plt.savefig(os.path.join(os.getcwd(), "clustered", person_name, "graph1.png"))
    # pprint.pprint(fim_path)
    # pprint.pprint(pred_label)

    for i in range(0, K):
        os.makedirs(os.path.join(os.getcwd(), "clustered", person_name, str(i)), exist_ok=True)
    for file_path, cluster in zip(fim_path, pred_label):
        os.link(file_path,
                os.path.join(os.getcwd(), "clustered", person_name, str(cluster), os.path.basename(file_path)))


    def imscatter(x, y, image_path, ax=None, zoom=1):
        if ax is None:
            ax = plt.gca()

        artists = []
        for order, (x0, y0, image) in enumerate(zip(x, y, image_path)):
            if order % 3 != 0:
                continue
            image = plt.imread(image)
            im = OffsetImage(image, zoom=zoom)
            ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
            artists.append(ax.add_artist(ab))
        return artists


    x = reduced[::3, 0]
    y = reduced[::3, 1]
    fig, ax = plt.subplots(figsize=(100, 100))
    imscatter(x, y, fim_path, ax=ax, zoom=.5)
    ax.plot(x, y, 'ko', alpha=0)
    ax.autoscale()
    plt.savefig(os.path.join(os.getcwd(), "clustered", person_name, "graph2.png"))

    plt.close("all")

    del fig
    del ax

    print("Image Output Time: " + str(time.time() - image_output_time))
