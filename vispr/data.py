"""Data loading functionality

"""
import glob
import os
import logging

import numpy as np
import h5py
from PIL import Image

logger = logging.getLogger(__name__)


def crop(img, i, j, h, w):
    return img.crop((j, i, j + w, i + h))


def center_crop(img, output_size):
    w, h = img.size
    th, tw = output_size
    i = int(round((h - th) / 2.))
    j = int(round((w - tw) / 2.))
    return crop(img, i, j, th, tw)


class AttrImage(object):
    def __init__(self, atpath):
        self._atpath = atpath

    def __getitem__(self, key):
        if isinstance(key, slice):
            key = range(*key.indices(len(self)))

        with h5py.File(self._atpath, 'r') as fd:
            def load_index(x):
                return fd['attribution'][x].mean(0)[::-1]
            if isinstance(key, (range, list, tuple, np.ndarray)):
                return [load_index(k) for k in key]
            else:
                return load_index(key)

    def __len__(self):
        with h5py.File(self._atpath, 'r') as fd:
            length = len(fd['attribution'])
        return length


class OrigImage(object):
    def __init__(self, inpath):
        """
        Parameters
        ----------
        inpath: str
            Path to a directory containing images: class_name/image_name.jpg
            or path to a file containing absolute paths to images.
        """
        self._dummy = Image.new('RGBA', (224, 224), color=(255, 0, 0, 255))
        self._fpath = inpath

        if os.path.isdir(inpath):
            self._index = sorted(glob.glob(os.path.join(inpath, '*/*')))
        else:
            with open(inpath, 'r') as f:
                self._index = sorted([x.strip() for x in f.readlines()])

    def _load_index(self, key):
        try:
            img = Image.open(self._index[key])
            img = center_crop(img, (224, 224))
            img = img.convert('RGB')
            img.putalpha(255)
        except FileNotFoundError:
            img = self._dummy
            logger.warning('File not found, using dummy: {}'.format(self._index[key]))
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
