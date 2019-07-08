#!/usr/bin/env python
import logging
import os
from os import path
from sys import stdout
from argparse import Namespace

import h5py
import numpy as np
import click
from sklearn.manifold import TSNE
from sklearn.cluster import k_means

from .spectral import SpectralEmbedding
from .affinity import SparseKNN

logger = logging.getLogger(__name__)


def csints(arg):
    return [int(s) for s in arg.split(',')]

@click.group(chain=True)
@click.argument('data', type=click.Path())
@click.option('--exname', default='default')
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--modify/--no-modify', default=False)
@click.option('--log', type=click.File(), default=stdout)
@click.option('-v', '--verbose', count=True)
@click.pass_context
def main(ctx, data, exname, overwrite, modify, log, verbose):
    logger.addHandler(logging.StreamHandler(log))
    logger.setLevel(logging.DEBUG if verbose > 0 else logging.INFO)

    defaults = {
        'data': data,
        'exname': exname,
        'modify': modify,
        'overwrite': overwrite,
    }
    ctx.default_map = dict(zip(('embed', 'cluster', 'tsne'), (defaults,)*3))
    ctx.ensure_object(Namespace)

@main.command()
@click.argument('attribution', type=click.Path())
@click.option('--label-filter', type=csints)
@click.option('--data', type=click.Path())
@click.option('--exname')
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--modify/--no-modify', default=False)
@click.option('--eigvals', type=int, default=32)
@click.option('--knn', type=int, default=10)
@click.pass_context
def embed(ctx, attribution, label_filter, exname, data, overwrite, modify, eigvals, knn):
    fout = data

    if not path.exists(fout) or modify:
        logger.info('Computing embedding: {}'.format(fout))
        with h5py.File(attribution, 'r') as fd:
            raw_label = fd['label'][:]
            if label_filter is None:
                #inds = slice(None)
                inds = np.arange(len(raw_label), dtype=np.uint32)
            else:
                inds, = np.nonzero(np.in1d(raw_label, label_filter))
                if not len(inds):
                    logger.error('No matches found for filter: %s'%str(label_filter))
                    return

            label = raw_label[inds]
            attr  = fd['attribution'][inds, :]

        #attr  = attr.mean(1)
        shape = attr.shape
        attr = attr.reshape(shape[0], np.prod(shape[1:]))

        os.makedirs(path.dirname(fout), exist_ok=True)


        eigval, eigvec = SpectralEmbedding(
            n_eigval=eigvals,
            affinity_fn=SparseKNN(k_neighbors=knn)
        )(attr)
        eigval, eigvec = (val.astype(np.float32) for val in (eigval, eigvec))

        inds = inds.astype(np.uint32)
        with h5py.File(fout, 'a') as fd:
            subfd = fd.require_group(exname)
            for key, val in zip(('index', 'eigenvalue', 'eigenvector'), (inds, eigval, eigvec)):
                if key in subfd:
                    if overwrite:
                        del subfd[key]
                    else:
                        logger.error('Key already exists and overwrite is disabled: %s'%key)
                        continue
                subfd[key] = val
        ctx.obj.ev = eigvec
    else:
        logger.info('File exists, not overwriting embedding: {}'.format(fout))

@main.command()
@click.option('--data', type=click.Path())
@click.option('--exname')
@click.option('--output', type=click.Path())
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--modify/--no-modify', default=False)
@click.option('--computed/--loaded', default=True)
@click.option('--eigvals', type=int, default=8)
@click.option('--clusters', type=csints, default='2,3,4,5')
@click.pass_context
def cluster(ctx, data, exname, output, overwrite, modify, computed, eigvals, clusters):
    fout = data if output is None else output

    if not path.exists(fout) or modify:
        logger.info('Computing clustering: {}'.format(fout))
        if computed and ('ev' in ctx.obj):
            ev = ctx.obj.ev
        else:
            try:
                with h5py.File(data, 'r') as fd:
                    subfd = fd.require_group(exname)
                    ev = subfd['eigenvector'][:]
            except KeyError:
                logger.error('Embedding must be either computed or already exist in data.')
                return

        llabels = []
        for k in clusters:
            _, lab, _ = k_means(ev[:, -eigvals:], k)
            llabels.append(lab.astype('uint8'))

        with h5py.File(fout, 'a') as fd:
            fdl = fd.require_group(exname + '/cluster')
            for kval, lab in zip(clusters, llabels):
                key = 'kmeans-%d'%kval
                if key in fdl:
                    if overwrite:
                        del fdl[key]
                    else:
                        logger.error('Key already exists and overwrite is disabled: %s'%key)
                        continue
                fdl[key] = lab
                fdl[key].attrs.create('k', kval, dtype=np.uint8)
                fdl[key].attrs.create('eigenvector', range(ev.shape[1] - eigvals, ev.shape[1]), dtype=np.uint32)
    else:
        logger.info('File exists, not overwriting clustering: {}'.format(fout))

@main.command()
@click.option('--data', type=click.Path())
@click.option('--exname')
@click.option('--output', type=click.Path())
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--modify/--no-modify', default=False)
@click.option('--computed/--loaded', default=True)
@click.option('--eigvals', type=int, default=8)
@click.pass_context
def tsne(ctx, data, exname, output, overwrite, modify, computed, eigvals):
    fout = data if output is None else output

    if not path.exists(fout) or modify:
        logger.info('Computing TSNE: {}'.format(fout))
        if computed and ('ev' in ctx.obj):
            ev = ctx.obj.ev
        else:
            try:
                with h5py.File(data, 'r') as fd:
                    subfd = fd.require_group(exname)
                    ev = subfd['eigenvector'][:]
            except KeyError:
                logger.error('Embedding must be either computed or already exist in data.')
                return

        tsne = TSNE().fit_transform(ev[:, -eigvals:])

        with h5py.File(fout, 'a') as fd:
            fdl = fd.require_group(exname + '/visualization')
            key = 'tsne'
            if key in fdl:
                if overwrite:
                    del fdl[key]
                else:
                    logger.error('Key already exists and overwrite is disabled: %s'%key)
                    return
            fdl[key] = tsne.astype(np.float32)
            fdl[key].attrs.create('eigenvector', range(ev.shape[1] - eigvals, ev.shape[1]), dtype=np.uint32)
    else:
        logger.info('File exists, not overwriting TSNE: {}'.format(fout))

if __name__ == '__main__':
    main()
