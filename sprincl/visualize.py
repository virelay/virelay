#!/usr/bin/env python
import logging

import numpy as np

from os import path

from matplotlib import pyplot as plt
from matplotlib import cm

logger = logging.getLogger(__name__)

def spray_visualize(data, ew, ev, centroid, cluster, emb, fpath, nevals, shape):
    def fname(desc):
        fdir, fbase = path.split(fpath)
        return path.join(fdir, '{}.{}.png'.format(fbase, desc))

    # Eigenvalue Plot
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.scatter(range(len(ew))[::-1], ew)
    fig.savefig(fname('eigenval'))
    plt.close(fig)

    # Examples for different clusters
    nexamples = 10
    height, width = shape
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
    vabs = np.abs(examples).max()
    ax.imshow(examples, cmap='seismic', vmin=-vabs, vmax=vabs)
    ax.set_xlabel('Examples')
    ax.set_ylabel('Clusters')
    sm = cm.ScalarMappable(norm=plt.Normalize(0, nevals), cmap='tab10')
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    fig.savefig(fname('examples'))
    plt.close(fig)

    # TSNE visualization
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.scatter(*emb.T, c=cluster, cmap='tab10', vmin=0, vmax=nevals)
    sm = cm.ScalarMappable(norm=plt.Normalize(0, nevals), cmap='tab10')
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    fig.savefig(fname('tsne'))
    plt.close(fig)

