import os
import json

import numpy as np
import h5py
import click


def append_input(fname, data, label):
    if not os.path.exists(fname):
        mkw = {'chunks': True, 'compression': 'gzip'}
        subshp = tuple(data.shape[1:])
        with h5py.File(fname, 'w') as fd:
            fd.create_dataset(
                'data', shape=(0,) + subshp, dtype='float32', maxshape=(None,) + subshp, **mkw
            )
            fd.create_dataset('label', shape=(0,), dtype='uint16', maxshape=(None,), **mkw)

    with h5py.File(fname, 'a') as fd:
        n = fd['data'].shape[0]
        nnew = data.shape[0]
        fd['data'].resize(n + nnew, axis=0)
        fd['label'].resize(n + nnew, axis=0)

        fd['data'][n:] = data
        fd['label'][n:] = label


def append_attribution(fname, attrib, out, label):
    if not os.path.exists(fname):
        mkw = {'chunks': True, 'compression': 'gzip'}
        subshp = tuple(attrib.shape[1:])
        nout = tuple(out.shape[1:])
        with h5py.File(fname, 'w') as fd:
            fd.create_dataset(
                'attribution', shape=(0,) + subshp, dtype='float32', maxshape=(None,) + subshp, **mkw
            )
            fd.create_dataset(
                'prediction', shape=(0,) + nout, dtype='float32', maxshape=(None,) + nout, **mkw
            )
            fd.create_dataset('label', shape=(0,), dtype='uint16', maxshape=(None,), **mkw)

    with h5py.File(fname, 'a') as fd:
        n = fd['attribution'].shape[0]
        nnew = attrib.shape[0]
        fd['attribution'].resize(n + nnew, axis=0)
        fd['prediction'].resize(n + nnew, axis=0)
        fd['label'].resize(n + nnew, axis=0)

        fd['attribution'][n:] = attrib
        fd['prediction'][n:] = out
        fd['label'][n:] = label


@click.command()
@click.argument('input-file')
@click.argument('attribution-file')
@click.argument('label-map-file')
@click.option('--num-classes', default=10)
@click.option('--num-samples', default=100)
@click.option('--overwrite/--append', default=False)
def main(
    input_file,
    attribution_file,
    label_map_file,
    num_classes,
    num_samples,
    overwrite
):

    label_map = [
        {
            'index': i,
            'word_net_id': f'{i:08d}',
            'name': f'Class {i:d}',
        } for i in range(num_classes)
    ]
    with open(label_map_file, 'w') as fd:
        json.dump(label_map, fd)

    if overwrite:
        for fname in (input_file, attribution_file):
            if os.exists(fname):
                os.remove(fname)

    for label_s in range(num_classes):
        data = np.random.uniform(0, 1, size=(num_samples, 3, 32, 32))
        label = np.array([label_s] * num_samples)

        attrib = np.random.uniform(-1, 1, size=(num_samples, 3, 32, 32))
        out = np.random.uniform(0, 1, size=(num_samples, num_classes))

        append_input(input_file, data, label)
        append_attribution(attribution_file, attrib, out, label)


if __name__ == '__main__':
    main()
