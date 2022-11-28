import math
import operator
import os.path
import shutil
import sys
from umap import UMAP
from sklearn.decomposition import PCA
import numpy
import numpy as np
import h5py as HDF5

[os.remove(os.path.join(os.getcwd(), "topK", f)) for f in os.listdir(os.path.join(os.getcwd(), "topK"))]

key_list: list[str] = list()
Dataset = HDF5.File(os.path.join(os.getcwd(), "embeddings.hdf5"))
# embeddings: numpy.ndarray = np.empty((len(Dataset.keys()), 512), np.float16)
embeddings: numpy.ndarray = np.empty((len(Dataset.keys()), 512), np.float16)
for i, key in enumerate(Dataset.keys()):
    key_list.append(key)
    embeddings[i] = Dataset[key][()]
print(embeddings.shape)

first_reduced = PCA(n_components=50).fit_transform(embeddings)
print("start UMAP")
second_reduced = UMAP(n_components=7).fit_transform(first_reduced)
print(second_reduced)

search_key = int(sys.argv[1])
print(key_list[search_key])
search_embeddings = second_reduced[search_key]
print(search_embeddings)
sort_list: list[tuple[int, float]] = list()
print("start Euclid")
for i, reduced_embedding in enumerate(second_reduced):
    sort_list.append((i, math.dist(search_embeddings, reduced_embedding)))
print("sort")
sorted_list = sorted(sort_list, key=operator.itemgetter(1))

for i, distance in sorted_list[:150]:
    filename: str = key_list[i]
    print(filename, distance)
    try:
        shutil.copyfile(os.path.join(os.getcwd(), "face_dataset", filename.split('=')[0], filename),
                        os.path.join(os.getcwd(), "topK", filename))
    except FileNotFoundError as e:
        print(e)
