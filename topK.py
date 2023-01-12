import pprint
import time
import cudf
import h5py
import os.path
import shutil
from cuml import UMAP, PCA
from cuml.neighbors import NearestNeighbors

[os.remove(os.path.join(os.getcwd(), "topK", f)) for f in os.listdir(os.path.join(os.getcwd(), "topK"))]

key_list: list[str]
# Dataset = HDF5.File(os.path.join(os.getcwd(), "embeddings.hdf5"))
# embeddings: numpy.ndarray = np.empty((len(Dataset.keys()), 512), np.float16)
# embeddings: numpy.ndarray = np.empty((len(Dataset.keys()), 512), np.float32)
# for i, key in enumerate(Dataset.keys()):
#     key_list.append(key)
#     embeddings[i] = Dataset[key][()]
fast_load = h5py.File(os.path.join(os.getcwd(), "fast_load.hdf5"), mode="r")
key_list = fast_load["keys"][()]
embeddings = fast_load["embeddings_array"][()]
fast_load.close()
print(embeddings.shape)

first_reduced = PCA(n_components=60).fit_transform(embeddings)
print("start UMAP")
second_reduced = UMAP(n_components=7).fit_transform(first_reduced)
# last_reduced = PCA(n_components=7).fit_transform(second_reduced)
last_reduced = second_reduced
print(last_reduced)
while True:
    start_time = time.time()
    print("Please input: ", end='')
    in_num = input()
    if not in_num.isdigit():
        continue
    [os.remove(os.path.join(os.getcwd(), "topK", f)) for f in os.listdir(os.path.join(os.getcwd(), "topK"))]
    search_key = int(in_num)
    if search_key > len(key_list):
        continue
    print(bytes(key_list[search_key]).decode('utf-8'))
    search_embeddings = last_reduced[search_key]
    print(search_embeddings)
    sort_list: list[tuple[int, float]] = list()
    print("start Euclid")
    # for i, reduced_embedding in enumerate(last_reduced):
    #     sort_list.append((i, math.dist(search_embeddings, reduced_embedding)))
    # print("sort")
    # sorted_list = sorted(sort_list, key=operator.itemgetter(1))
    KNN = NearestNeighbors(n_neighbors=50, algorithm="brute", metric="manhattan").fit(last_reduced)
    X_cudf = cudf.DataFrame(last_reduced[search_key].reshape(1, -1))
    distances, indices = KNN.kneighbors(X_cudf)
    print(time.time() - start_time)

    # print(X_cudf)
    # print(distances.to_pandas())
    # print(indices)
    # a = indices
    # print(a.values[0])
    order: int = 0
    # sorted_list[:150]
    person_list = dict()
    for i, distance in zip(indices.values[0].tolist(), distances.values[0].tolist()):
        order += 1
        filename: str = bytes(key_list[i]).decode('utf-8')
        # print(order, filename, distance)
        person_name = filename.split('=')[0]
        if person_name not in person_list:
            person_list[person_name] = 1
        else:
            person_list[person_name] += 1

        try:
            shutil.copyfile(os.path.join(os.getcwd(), "face_dataset", filename.split('=')[0], filename),
                            os.path.join(os.getcwd(), "topK", filename))
        except FileNotFoundError as e:
            print(e)
    pprint.pprint(sorted(person_list.items(), key=lambda x: -x[1])[:10])
