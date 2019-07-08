import logging

import numpy as np
from scipy import sparse as sp

logger = logging.getLogger(__name__)


class Affinity(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, distance):
        raise NotImplementedError

class SparseKNN(Affinity):
    def __init__(self, *args, k_neighbours=10, symmetric=True, **kwargs):
        super().__init__(*args, **kwargs)
        self._k_neighbours = k_neighbours
        self._symmetric = symmetric

    def __call__(self, distance):
        k = self._k_neighbours
        n = distance.shape[0]

        k = k if k < (n-1) else (n-1)
        cols = distance.argsort(1)[:, 1:k+1]
        rows = np.mgrid[:n, :k][0]
        vals = np.ones((n, k), dtype=distance.dtype)
        affinity = sp.csr_matrix((vals.flat, (rows.flat, cols.flat)), shape=(n, n))

        if self._symmetric:
            affinity = (affinity + affinity.T) / 2.
        affinity = affinity
        return affinity

class RadialBasisFunction(Affinity):
    def __init__(self, *args, sigma=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self._sigma = sigma

    def __call__(self, distance):
        sigma = self._sigma
        affinity = np.exp(-distance/(2*sigma**2))
        return affinity

