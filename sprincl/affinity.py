import logging

import numpy as np
from scipy import sparse as sp

logger = logging.getLogger(__name__)


class Affinity(object):
    """Base class for Affinity (Similarity) classes.

    Each subclass implements a __call__ function to compute its corresponding affinity matrix of some data.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, distance):
        """Abstract function to compute affinity matrix.

        Parameters
        ----------
        distance : :obj:`numpy.ndarray`
            Distance matrix used to compute affinity matrix.

        Raises
        ------
        NotImplementedError
            Abstract method

        """
        raise NotImplementedError

class SparseKNN(Affinity):
    """Sparse K-Nearest-Neighbors affinity

    """
    def __init__(self, *args, k_neighbors=10, symmetric=True, **kwargs):
        """Initialize Parameters for KNN computation.

        Parameters
        ----------
        k_neighbors : int
            Number of neighbors to consider.
        symmetrix : bool
            If `True`, Affinity matrix is set to the mean of itself and itself transposed.

        """
        super().__init__(*args, **kwargs)
        self._k_neighbors = k_neighbors
        self._symmetric = symmetric

    def __call__(self, distance):
        """Compute Sparse K-Nearest-Neighbors affinity matrix.

        Parameters
        ----------
        distance : :obj:`numpy.ndarray`
            Distance matrix used to compute affinity matrix.

        Returns
        ------
        :obj:`sp.csr_matrix`
            Sparse CSR representation of KNN affinity matrix

        """
        k = self._k_neighbors
        # number of samples
        n = distance.shape[0]

        # silently use maximum number of neighbors if there are more samples than k
        k = k if k < (n-1) else (n-1)

        # set up indices for sparse representation of nearest neighbors
        cols = distance.argsort(1)[:, 1:k+1]
        rows = np.mgrid[:n, :k][0]
        # existing edges are denoted with ones
        vals = np.ones((n, k), dtype=distance.dtype)
        affinity = sp.csr_matrix((vals.flat, (rows.flat, cols.flat)), shape=(n, n))

        # make the affinity matrix symmetric
        if self._symmetric:
            affinity = (affinity + affinity.T) / 2.
        return affinity

class RadialBasisFunction(Affinity):
    """Radial Basis Function affinity

    """
    def __init__(self, *args, sigma=1.0, **kwargs):
        """Initialize RBF affinity

        Parameters
        ----------
        sigma : float
            RBF scale

        """
        super().__init__(*args, **kwargs)
        self._sigma = sigma

    def __call__(self, distance):
        """Compute Radial Basis Function affinity matrix.

        Parameters
        ----------
        distance : :obj:`numpy.ndarray`
            Distance matrix used to compute affinity matrix.

        Returns
        ------
        :obj:`np.ndarray`
            Dense RBF affinity matrix

        """
        sigma = self._sigma
        affinity = np.exp(-distance/(2*sigma**2))
        return affinity

