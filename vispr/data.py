import os

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

class OrigImage(object):
    def __init__(self, inpath):
        dmatch = re.compile(r'n\d{8}\.tar').fullmatch
        fmatch = re.compile(r'n\d{8}_\d+\.JPEG').fullmatch
        self._fpath = inpath
        self._index = list(
            os.path.join(dname, fname)
            for dname in sorted(filter(dmatch, os.listdir(inpath)))
            for fname in sorted(filter(fmatch, os.listdir(dname)))
        )

    def _load_index(self, key):
        img = Image.open(self._index[key])
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

