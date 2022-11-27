import os.path
from umap import UMAP
from sklearn.decomposition import PCA, KernelPCA
import numpy
import numpy as np
import h5py as HDF5

key_list: list[str] = list()
Dataset = HDF5.File(os.path.join(os.getcwd(), "embeddings.hdf5"))
embeddings: numpy.ndarray = np.empty((len(Dataset.keys()), 512), np.float16)
for i, key in enumerate(Dataset.keys()):
    key_list.append(key)
    embeddings[i] = Dataset[key][()]
print(embeddings.shape)

first_reduced = PCA(n_components=70).fit_transform(embeddings)
second_reduced = UMAP(n_components=7).fit_transform(first_reduced)
print(second_reduced)
