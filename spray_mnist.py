#!/usr/bin/env python
import logging
import json

import h5py
import numpy as np

from os import path
from argparse import ArgumentParser

from matplotlib import pyplot as plt
from matplotlib import cm
#from scipy.linalg import eigh
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

def main():
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('heatmaps')
    parser.add_argument('-p', '--plotprefix', default='plot/')
    parser.add_argument('-c', '--checkpoint', default='mnist.spectral.{:02d}.h5')
    parser.add_argument('-w', '--overwrite', action='store_true')
    parser.add_argument('--nneighbours', type=int, default=10)
    parser.add_argument('--nevals', type=int, default=10)
    args = parser.parse_args()

    with h5py.File('mnist.h5', 'r') as fd:
        fdata = fd['data'][:]
        flabel = fd['label'][:]
    nclasses = 10
    height = 28
    width = 28

    nneighbours = args.nneighbours
    nevals = args.nevals

    for target in range(nclasses):
        fname = args.checkpoint.format(target)
        data = fdata[flabel == target]
        data = data.reshape(data.shape[0], np.prod(data.shape[1:]))
        if not path.exists(fname) or args.overwrite:
            logger.info('Computing {}'.format(fname))
            condist = pdist(data)
            dist = squareform(condist)
            ew, ev = spectral(dist, neighbours=nneighbours, k=nevals)

            centroid, _, _ = k_means(ev, nneighbours)
            cluster = cdist(centroid, dist @ ev).argmax(0)

            emb = TSNE(metric='precomputed').fit_transform(dist)
            with h5py.File(fname, 'w') as fd:
                fd['ew'] = ew
                fd['ev'] = ev
                fd['centroid'] = centroid
                fd['cluster'] = cluster
                fd['emb'] = emb
        else:
            logger.info('Loading {}'.format(fname))
            with h5py.File(fname, 'r') as fd:
                ew = fd['ew'][:]
                ev = fd['ev'][:]
                centroid = fd['centroid'][:]
                cluster = fd['cluster'][:]
                emb = fd['emb'][:]

        belongs = (cluster[None] == np.arange(nevals)[:, None]).sum(1)
        logger.info('Samples in clusters: {}'.format(", ".join([str(n) for n in belongs])))

        logger.info('Visualizing {}'.format(fname))

        # Eigenvalue Plot
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.scatter(range(len(ew))[::-1], ew)
        fig.savefig(args.plotprefix + 'eigenval.{:02d}.png'.format(target))
        plt.close(fig)

        # Examples for different clusters
        nexamples = 10
        examples = np.zeros((nevals, nexamples, height, width))
        nuniq = 0
        for nc in range(nevals):
            sub = data[cluster == nc][:nexamples]
            rlen = sub.shape[0]
            if rlen > 0:
                examples[nc, :rlen].flat = sub.flat
        examples = examples[::-1].transpose(0, 2, 1, 3).reshape(nevals * height, nexamples * width)
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.imshow(examples, cmap='hot')
        ax.set_xlabel('Examples')
        ax.set_ylabel('Clusters')
        sm = cm.ScalarMappable(norm=plt.Normalize(0, nevals), cmap='tab10')
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax)
        fig.savefig(args.plotprefix + 'examples.{:02d}.png'.format(target))
        plt.close(fig)

        # TSNE visualization
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.scatter(*emb.T, c=cluster, cmap='tab10', vmin=0, vmax=nevals)
        sm = cm.ScalarMappable(norm=plt.Normalize(0, nevals), cmap='tab10')
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax)
        fig.savefig(args.plotprefix + 'tsne.{:02d}.png'.format(target))
        plt.close(fig)


if __name__ == '__main__':
    main()
