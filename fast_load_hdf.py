import h5py
from h5py import File
import os.path
import numpy as np

Dataset = File(name=os.path.join(os.getcwd(), "embeddings.hdf5"), mode="r")
embeddings: np.ndarray = np.empty((len(Dataset.keys()), 512), np.float32)
key_list: list[str] = list()

for i, key in enumerate(Dataset.keys()):
    key_list.append(str(key))
    embeddings[i] = Dataset[key][()]
print(embeddings.shape)

fast_hdf = File(name="fast_load.hdf5", mode="w")
fast_hdf.create_dataset(name="embeddings_array", data=embeddings)
fast_hdf.create_dataset(name="keys", data=key_list)
fast_hdf.close()
