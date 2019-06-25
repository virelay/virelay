import os

import h5py
import numpy as np
from PIL import Image

def crop(img, i, j, h, w):
    return img.crop((j, i, j + w, i + h))

def center_crop(img, output_size):
    w, h = img.size
    th, tw = output_size
    i = int(round((h - th) / 2.))
    j = int(round((w - tw) / 2.))
    return crop(img, i, j, th, tw)

def get_attrib(atpath, cat):
    fname = os.path.join(atpath, 'train_set.{}.dtd.h5'.format(cat))
    with h5py.File(fname, 'r') as fp:
        attrib = fp['attribution'][:].mean(1)
        pred = fp['prediction'][:]
    attrib /= attrib.max(0)
    return attrib[:, ::-1], pred

def get_clu(anpath, cat):
    clupath = os.path.join(anpath, '{}.clu.h5'.format(cat))
    with h5py.File(clupath, 'r') as fp:
        kcluster = fp['kcluster'][:]
        label = fp['label'][:]
    return kcluster, label

def get_ew(anpath, cat):
    clupath = os.path.join(anpath, '{}.emb.h5'.format(cat))
    with h5py.File(clupath, 'r') as fp:
        ew = fp['ew'][:]
    return ew

def get_tsne(anpath, cat):
    tsnpath = os.path.join(anpath, '{}.tsn.h5'.format(cat))
    with h5py.File(tsnpath, 'r') as fp:
        tsne = fp['tsne'][:]
    return tsne

class OrigImage(object):
    def __init__(self, inpath, cat):
        self._fpath = os.path.join(inpath, '{}.tar'.format(cat))
        self._items = sorted([fname for fname in os.listdir(self._fpath) if fname[-5:] == '.JPEG'])

    def _load_index(self, key):
        img = Image.open(os.path.join(self._fpath, self._items[key]))
        img = center_crop(img, (224, 224))
        img = img.convert('RGB')
        img.putalpha(255)
        return np.array(img)[::-1]

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        if isinstance(key, slice):
            key = range(*key.indices(len(self)))
        if isinstance(key, (range, list, tuple, np.ndarray)):
            return [self._load_index(k) for k in key]
        else:
            return self._load_index(key)

