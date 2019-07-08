import logging

import numpy as np
from scipy import sparse as sp

logger = logging.getLogger(__name__)


def A1ifmat(x):
    """Return flat representation of x if x is a :obj:`numpy.matrix`

    Parameters
    ----------
    x : :obj:`numpy.ndarray` or :obj:`numpy.matrix`
        Object to convert if necessary

    Returns
    -------
    :obj:`numpy.ndarray`
        Matrix as flat :obj:`numpy.ndarray` if `x` was a :obj:`numpy.matrix`, else `x`

    """
    return x.A1 if isinstance(x, np.matrix) else x

def laplacian_normal_symmetric(affinity):
    """Normalized Symmetric Graph Laplacian

    Parameters
    ----------
    affinity : :obj:`sp.csr_matrix` or :obj:`np.ndarray`
        Graph affinity/similarity matrix.

    Returns
    -------
    :obj:`sp.csr_matrix`
        Sparse representation of a symmetric graph laplacian matrix

    """
    deg = sp.diags(A1ifmat(affinity.sum(1))**-.5, 0)
    lap = deg @ affinity @ deg
    return lap

def laplacian_normal_randomwalk(affinity):
    """Normalized Random Walk Graph Laplacian

    Parameters
    ----------
    affinity : :obj:`sp.csr_matrix` or :obj:`np.ndarray`
        Graph affinity/similarity matrix.

    Returns
    -------
    :obj:`sp.csr_matrix`
        Sparse representation of a random walk graph laplacian matrix

    """
    deg = sp.diags(A1ifmat(affinity.sum(1))**-1., 0)
    lap = deg @ affinity
    return lap

