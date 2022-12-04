import os.path
import pprint
import h5py

HDF5 = h5py.File(name="embeddings.hdf5", mode='r')

for i in HDF5.keys():
    print(i)
