import numpy as np
from scipy.sparse.linalg import eigsh

from .base import processor

class Embedding(Processor):
    pass

class EigenDecomposition(Embedding):
    """Eigenvalue Decomposition

    """
    n_eigval = Param(int, 32)
    which = Param(str, 'LM')
    normalize = Param(bool, True)

    def function(self, data):
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
        data and return one minus the eigenvalue.

        """
        eigval, eigvec = eigsh(data, k=self._n_eigval, which='LM')
        eigval = 1. - eigval

        if self.normalize:
            eigvec /= np.linalg.norm(eigvec, axis=1, keepdims=True)
        return eigval, eigvec

