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
        self._f = h5py.File(atpath, 'r')

    def _load_index(self, key):
        attribution = self._f['attribution'][key].mean(0)[::-1]
        return attribution

    def __getitem__(self, key):
        if isinstance(key, slice):
            key = range(*key.indices(len(self)))
        if isinstance(key, (range, list, tuple, np.ndarray)):
            return [self._load_index(k) for k in key]
        else:
            return self._load_index(key)

    def __len__(self):
        length = len(self._f['attribution'])
        return length

    def close(self):
        self._f.close()

class OrigImage(object):
    def __init__(self, inpath):
        self._dummy = Image.new('RGBA', (224, 224), color=(255, 0, 0, 255))
        self._fpath = inpath
        image_path_file = inpath + '_paths.txt'
        dir_path = os.path.dirname(inpath)
        if os.path.exists(image_path_file):
            with open(image_path_file, 'r') as f:
                self._index = sorted([os.path.join(dir_path, x.strip()) for x in f.readlines()])
        else:
            raise NotImplementedError('Create image_path_file: {}'.format(image_path_file))

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

