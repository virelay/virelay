import os
import re
import logging

import numpy as np
import h5py
from PIL import Image, ImageDraw, ImageFont

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

    def _load_index(self, key):
        with h5py.File(self._atpath, 'r') as fd:
            attribution = fd['attribution'][key].mean(0)[::-1]
        return attribution

    def __getitem__(self, key):
        if isinstance(key, slice):
            key = range(*key.indices(len(self)))
        if isinstance(key, (range, list, tuple, np.ndarray)):
            return [self._load_index(k) for k in key]
        else:
            return self._load_index(key)

    def __len__(self):
        with h5py.File(self._atpath, 'r') as fd:
            length = len(fd['attribution'])
        return length

class OrigImage(object):
    def __init__(self, inpath):
        dmatch = re.compile(r'n\d{8}\.tar').fullmatch
        fmatch = re.compile(r'n\d{8}_\d+\.JPEG').fullmatch

        self._dummy = Image.new('RGBA', (224, 224), color=(255, 0, 0, 255))

        self._fpath = inpath
        self._index = list(
            os.path.join(inpath, dname, fname)
            for dname in sorted(filter(dmatch, os.listdir(inpath)))
            for fname in sorted(filter(fmatch, os.listdir(os.path.join(inpath, dname))))
        )

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

