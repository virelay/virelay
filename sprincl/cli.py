#!/usr/bin/env python
import logging

import h5py
import numpy as np

from os import path
from argparse import ArgumentParser

logger = logging.getLogger(__name__)

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
    shape = (28, 28)

    for target in range(nclasses):
        fname = args.checkpoint.format(target)
        data = fdata[flabel == target]
        data = data.reshape(data.shape[0], np.prod(data.shape[1:]))
        if not path.exists(fname) or args.overwrite:
            logger.info('Computing {}'.format(fname))
            ew, ev, centroid, cluster, emb = spray_compute(data, args.nneighbours, args.nevals)
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

        belongs = (cluster[None] == np.arange(args.nevals)[:, None]).sum(1)
        logger.info('Samples in clusters: {}'.format(", ".join([str(n) for n in belongs])))

        logger.info('Visualizing {}'.format(fname))
        spray_visualize(data, ew, ev, centroid, cluster, emb, target, args.nevals, args.plotprefix, shape=shape)


if __name__ == '__main__':
    main()
