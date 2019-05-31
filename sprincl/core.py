#!/usr/bin/env python
import logging

import numpy as np

from scipy.spatial.distance import cdist, pdist, squareform
from scipy import sparse as sp
from scipy.sparse.linalg import eigsh
from sklearn.cluster import k_means
from sklearn.manifold import TSNE

logger = logging.getLogger(__name__)

def spknn(dist, k=10, ones=False):
    n = dist.shape[0]
    k = k if k<n else n
    cols = dist.argsort(1)[:, :k]
    rows = np.mgrid[:n, :k][0]
    if ones:
        vals = dist[rows, cols]
    else:
        vals = np.ones((n, k), dtype=dist.dtype)
    retval = sp.csr_matrix((vals.flat, (rows.flat, cols.flat)), shape=(n, n))
    return retval

def spectral(dist, neighbours=10, k=10, sigma=1):
    if neighbours is not None:
        sim = spknn(dist, k=neighbours, ones=True)
        sim = (sim + sim.T) / 2.
        deg = sp.diags(sim.sum(1).A1**-.5, 0)
    else:
        sim = np.exp(-dist/(2*sigma**2))
        deg = sp.diags(sim.sum(1)**-.5, 0)
    #deg = sp.diags(sim.sum(1))
    #lap = np.eye(len(deg)) - (np.linalg.inv(deg)) @ sim
    lap = deg @ sim @ deg
    ew, ev = eigsh(lap, k=k, which='LM')
    ew = 1. - ew
    ev /= np.linalg.norm(ev, axis=1, keepdims=True)
    return ew, ev

def spray_compute(data, nneighbours=10, nevals=10):
    condist = pdist(data)
    dist = squareform(condist)
    ew, ev = spectral(dist, neighbours=nneighbours, k=nevals)

    centroid, _, _ = k_means(ev, nneighbours)
    specspac = dist @ ev
    cluster = cdist(centroid, specspac).argmax(0)

    emb = TSNE().fit_transform(specspac)
    return ew, ev, centroid, cluster, emb
