import logging

import numpy as np

from scipy.spatial.distance import pdist, squareform
from scipy.sparse.linalg import eigsh
from sklearn.cluster import KMeans

from .affinity import SparseKNN
from .laplacian import laplacian_normal_symmetric

logger = logging.getLogger(__name__)


class SpectralEmbedding(object):
    def __init__(self, *args, n_eigval=32,
                 pairwise_distance_fn=(lambda x: squareform(pdist(x))),
                 affinity_fn=(lambda x: SparseKNN(k_neighbours=10, symmetric=True)(x)),
                 laplacian_fn=laplacian_normal_symmetric,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._pairwise_distance_fn = pairwise_distance_fn
        self._affinity_fn = affinity_fn
        self._laplacian_fn = laplacian_fn
        self._n_eigval = n_eigval

    def __call__(self, data):
        distance = self._pairwise_distance_fn(data)
        affinity = self._affinity_fn(distance)
        laplacian = self._laplacian_fn(affinity)
        eigval, eigvec = eigsh(laplacian, k=self._n_eigval, which='LM')
        eigval = 1. - eigval
        eigvec /= np.linalg.norm(eigvec, axis=1, keepdims=True)
        return eigval, eigvec

class SpectralClustering(SpectralEmbedding):
    def __init__(self, *args, clustering_fn=(lambda x: KMeans(n_clusters=8).fit_predict(x)), **kwargs):
        super().__init__(*args, **kwargs)
        self._clustering_fn = clustering_fn

    def __call__(self, data):
        eigval, eigvec = super()(data)
        label = self._clustering_fn(eigvec)
        return ew, ev, label
