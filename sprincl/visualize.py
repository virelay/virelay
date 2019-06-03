#!/usr/bin/env python
import logging

import numpy as np

from os import path

from matplotlib import pyplot as plt
from matplotlib import cm

logger = logging.getLogger(__name__)

def spray_visualize(data, ew, ev, cluster, tsne, fpath, nevals, shape, dpi=300):
    fdir, fbase = path.split(fpath)
    fbase, _ = path.splitext(fbase)
    def fname(desc):
        return path.join(fdir, '{}.{}.png'.format(fbase, desc))

    # Eigenvalue Plot
    fig = plt.figure(figsize=(2.4, 4.8))
    ax = plt.subplot(111)
    ax.scatter(range(len(ew))[::-1], ew)
    fig.savefig(fname('eigenval'), bbox_inches='tight', dpi=dpi)
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
    fig = plt.figure(figsize=(6.4, 4.8))
    ax = plt.subplot(111)
    vabs = np.abs(examples).max()
    ax.imshow(examples, cmap='seismic', vmin=-vabs, vmax=vabs, interpolation='nearest')
    ax.set_xlabel('Examples')
    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_ylabel('Clusters')
    ax.set_yticks([])
    ax.set_yticklabels([])
    sm = cm.ScalarMappable(norm=plt.Normalize(0, nevals), cmap='tab10')
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    fig.savefig(fname('examples'), bbox_inches='tight', dpi=dpi)
    plt.close(fig)

    # TSNE visualization
    fig = plt.figure(figsize=(4.8, 4.8))
    ax = plt.subplot(111)
    ax.scatter(*tsne.T, c=cluster, cmap='tab10', vmin=0, vmax=nevals)
    sm = cm.ScalarMappable(norm=plt.Normalize(0, nevals), cmap='tab10')
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    fig.savefig(fname('tsne'), bbox_inches='tight', dpi=dpi)
    plt.close(fig)

