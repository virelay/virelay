import logging

import numpy as np
from scipy import sparse as sp

logger = logging.getLogger(__name__)


def A1ifmat(x):
    return x.A1 if isinstance(x, np.matrix) else x

def laplacian_normal_symmetric(affinity):
    deg = sp.diags(A1ifmat(affinity.sum(1))**-.5, 0)
    lap = deg @ affinity @ deg
    return lap

def laplacian_normal_randomwalk(affinity):
    deg = sp.diags(A1ifmat(affinity.sum(1))**-1., 0)
    lap = deg @ affinity
    return lap

