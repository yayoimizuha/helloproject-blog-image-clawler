import os.path

import numpy

from sklearn.decomposition import PCA

import h5py

file = h5py.File(name=os.path.join(os.getcwd(), "embeddings.hdf5"), mode='a')
file256 = h5py.File(name=os.path.join(os.getcwd(), "embeddings_256.hdf5"), mode='a')

for i in file.keys():
    print(file[i].dtype)
    print(file[i].shape)
    break
with open("embeddings.csv", mode="w") as f:
    f.write('\n'.join([i + ',' + ','.join(['{:.5f}'.format(num) for num in file[i][()].tolist()]) for i in file.keys()]))

exit(0)
data = []
for i in file.keys():
    data.append(file[i][()])

data = numpy.array(data)

data = PCA(n_components=256).fit_transform(data)

for compacted, name in zip(data, file):
    file256.create_dataset(name=name, data=compacted)

for i in file256.keys():
    print(i)
    # print(file256[i].shape)
    # break
file.close()
file256.close()
