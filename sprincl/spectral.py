import logging

import numpy as np

from scipy.spatial.distance import pdist, squareform
from scipy.sparse.linalg import eigsh
from sklearn.cluster import KMeans

from .affinity import SparseKNN
from .laplacian import laplacian_normal_symmetric

logger = logging.getLogger(__name__)


class SpectralEmbedding(object):
    """Spectral Embedding with custom pipeline

    """
    def __init__(self, *args, n_eigval=32,
                 preprocessing_fn=(lambda x: x),
                 pairwise_distance_fn=(lambda x: squareform(pdist(x))),
                 affinity_fn=(lambda x: SparseKNN(k_neighbours=10, symmetric=True)(x)),
                 laplacian_fn=laplacian_normal_symmetric,
                 **kwargs):
        """Set number of eigenvalues and functions for spectral embedding

        Parameters
        ----------
        n_eigval : int, optional
            Number of smallest eigenvalues of the graph laplacian to compute.
        preprocessing_fn : callable, optional
            data pre-processing function of signature: (data : :obj:`numpy.ndarray`,) -> :obj:`numpy.ndarray`
        pairwise_distance_fn : callable, optional
            pairwise distance function of signature: (data : :obj:`numpy.ndarray`,) -> :obj:`numpy.ndarray`
        affinity_fn : callable, optional
            affinity function of signature: (distance : :obj:`numpy.ndarray`,) -> :obj:`numpy.ndarray`
        laplacian_fn : callable, optional
            laplacian function of signature: (distance : :obj:`numpy.ndarray`,) -> :obj:`numpy.ndarray`

        Note
        ----
        Pre-computed distance matrices can be supplied by passing `pairwise_distance_function`=(lambda x: x).
        Pre-computed affinity matrices can be supplied by additionally passing `affinity_fn`=(lambda x: x).
        Pre-computed graph laplacian matrices can be supplied by further passing `laplacian_fn`=(lambda x: x).

        """
        super().__init__(*args, **kwargs)
        self._pairwise_distance_fn = pairwise_distance_fn
        self._affinity_fn = affinity_fn
        self._laplacian_fn = laplacian_fn
        self._n_eigval = n_eigval

    def __call__(self, data):
        """Compute spectral embedding of `data`

        Parameters
        ----------
        data : :obj:`numpy.ndarray`
            data with samples in rows

        Returns
        -------
        :obj:`numpy.ndarray`
            Eigenvalues for spectral embedding
        :obj:`numpy.ndarray`
            Spectral embedding (eigenvectors)

        Note
        ----
        We use the fact that (I-A)v = (1-λ)v and thus compute the largest eigenvalues of the identity minus the
        laplacian and return one minus the eigenvalue.

        """
        processed = self._preprocessing_fn(data)
        distance = self._pairwise_distance_fn(processed)
        affinity = self._affinity_fn(distance)
        laplacian = self._laplacian_fn(affinity)

        eigval, eigvec = eigsh(laplacian, k=self._n_eigval, which='LM')
        eigval = 1. - eigval

        eigvec /= np.linalg.norm(eigvec, axis=1, keepdims=True)
        return eigval, eigvec

class SpectralClustering(SpectralEmbedding):
    """Clustering on a spectral embedding

    """
    def __init__(self, *args, clustering_fn=(lambda x: KMeans(n_clusters=8).fit_predict(x)), **kwargs):
        """Set parameters for spectral embedding and clustering function

        Parameters
        ----------
        clustering_fn : callable, optional
            label-returning clustering function of signature:
            (embedding : :obj:`numpy.ndarray`,) -> :obj:`numpy.ndarray`
        **kwargs
            Keyword arguments for `SpectralEmbedding`

        """
        super().__init__(*args, **kwargs)
        self._clustering_fn = clustering_fn

    def __call__(self, data):
        """Compute spectral embedding of `data`

        Parameters
        ----------
        data : :obj:`numpy.ndarray`
            data with samples in rows

        Returns
        -------
        :obj:`numpy.ndarray`
            Eigenvalues for spectral embedding
        :obj:`numpy.ndarray`
            Spectral embedding (eigenvectors)
        :obj:`numpy.ndarray`
            Labels of clustering on spectral embedding

        """
        eigval, eigvec = super()(data)
        label = self._clustering_fn(eigvec)
        return ew, ev, label
