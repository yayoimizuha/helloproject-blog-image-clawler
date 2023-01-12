from numba import njit
from h5py import File
from os import path, getcwd

fast_load = File(path.join(getcwd(), "fast_load.hdf5"), mode="r")
key_list = fast_load["keys"][()]
while True:
    keyword = input("input search keyword: ")
    for i, name in enumerate(key_list):
        if keyword in bytes(name).decode('utf-8'):
            print(i, bytes(name).decode('utf-8'))
