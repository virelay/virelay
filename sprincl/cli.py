#!/usr/bin/env python
import logging
import os

import h5py
import numpy as np
import click

from os import path
from argparse import Namespace

from sklearn.manifold import TSNE
from sklearn.cluster import k_means

from .core import spectral_clustering, spectral_embedding
from .visualize import spray_visualize

logger = logging.getLogger(__name__)

def csints(arg):
    return [int(s) for s in arg.split(',')]

@click.group(chain=True)
@click.option('--log', type=click.File(), default=stdout)
@click.option('-v', '--verbose', count=True)
@click.pass_context
def main(ctx, log, verbose, threads, device):
    logger.addHandler(logging.FileHandler(log))
    logger.setLevel(logging.DEBUG if verbose > 0 else logging.INFO)

    ctx.ensure_object(Namespace)

@main.command()
@click.argument('attribution', type=click.Path())
@click.argument('embedding', type=click.Path())
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--eigvals', type=int, default=32)
@click.option('--knn', type=int, default=10)
def embed():
    if not path.exists(embedding) or overwrite:
        logger.info('Computing embedding: {}'.format(embedding))
        with h5py.File(attribution, 'r') as fd:
            data  = fd['attribution'][:]
            label = fd['label'][:]

        data  = data.mean(1)
        shape = data.shape
        data = data.reshape(shape[0], np.prod(shape[1:]))

        os.makedirs(path.dirname(embedding), exist_ok=True)

        ew, ev = spectral_embedding(data, args.nneighbours, args.nevals, precomputed=False)
        with h5py.File(embedding, 'w') as fd:
            fd['ew'] = ew
            fd['ev'] = ev
    else:
        logger.info('File exists, not overwriting embedding: {}'.format(embedding))

@main.command()
@click.argument('embedding', type=click.Path())
@click.argument('clustering', type=click.Path())
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--eigvals', type=int, default=8)
@click.option('--knn', type=csints, default=[2, 3, 4, 5])
def cluster(embedding, clustering, overwrite, eigvals, knn):
    if not path.exists(clustering) or overwrite:
        logger.info('Computing clustering: {}'.format(clustering))
        with h5py.File(embedding, 'r') as fd:
            ev = fd['ev'][:]

        llabels = []
        for k in args.nclusters:
            _, lab, _ = k_means(ev[:, -eigvals:], k)
            llabels.append(lab)

        label = np.stack(llabels).astype('uint8')
        kcluster = np.array(args.nclusters, dtype='uint8')

        with h5py.File(clustering, 'w') as fd:
            fd['label'] = label
            fd['kcluster'] = kcluster

        #belongs = (label[None] == np.arange(eigvals)[:, None]).sum(1)
        #logger.info('Samples in clusters: {}'.format(", ".join([str(n) for n in belongs])))

    else:
        logger.info('File exists, not overwriting clustering: {}'.format(clustering))

@main.command()
@click.argument('embedding', type=click.Path())
@click.argument('tsne', type=click.Path())
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--eigvals', type=int, default=8)
def tsne(embedding, tsne, overwrite, eigvals):
    if not path.exists(tsne) or overwrite:
        logger.info('Computing TSNE: {}'.format(tsne))
        with h5py.File(embedding, 'r') as fd:
            ev = fd['ev'][:]

        tsne = TSNE().fit_transform(ev[:, -eigvals:])

        with h5py.File(tsne, 'w') as fd:
            fd['tsne'] = tsne
    else:
        logger.info('File exists, not overwriting TSNE: {}'.format(embedding))

@click.argument('attribution', type=click.Path())
@click.argument('embedding', type=click.Path())
@click.argument('clustering', type=click.Path())
@click.argument('tsne', type=click.Path())
@click.argument('output', type=click.Path())
@click.option('--knn', type=int, default=2)
def visualize(embedding, clustering, tsne, output):
    logger.info('Visualizing: {}'.format(output))
    with h5py.File(attribution, 'r') as fd:
        data  = fd['attribution'][:]
        label = fd['label'][:]

    data  = data.mean(1)
    shape = data.shape
    data = data.reshape(shape[0], np.prod(shape[1:]))

    os.makedirs(path.dirname(embedding), exist_ok=True)

    with h5py.File(embedding, 'r') as fd:
        ev = fd['ev'][:]
        ew = fd['ew'][:]
    with h5py.File(clustering, 'r') as fd:
        label = fd['label']
        kcluster = fd['kcluster']
    with h5py.File(tsne, 'r') as fd:
        tsne = fd['tsne']

    logger.info('Visualizing {}'.format(embedding))
    assert (kcluster == knn).any()
    spray_visualize(data, ew, ev, label[(kcluster == knn).argmax()], tsne, output, knn, data.shape[1:])

if __name__ == '__main__':
    main()
