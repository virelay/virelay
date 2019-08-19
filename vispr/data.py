"""Utility functions and classes for handling the loading of data."""

import glob
import os
import logging

import numpy as np
import h5py
from PIL import Image

LOGGER = logging.getLogger(__name__)


def crop(image, top, left, height, width):
    """
    Crops the specified image to the specified dimensions.

    Parameters:
    -----------
        image: PIL.Image
            The image that is to be cropped.
        top: int
            The position on the y-axis from which to crop.
        left: int
            The position on the x-axis from which to crop.
        height: int
            The height of the resulting image.
        width: int
            The width of the resulting image.

    Returns:
    --------
        PIL.Image
            Returns the cropped image.
    """

    return image.crop((left, top, left + width, top + height))


def center_crop(image, output_size):
    """
    Crops the specified image to the specified size using the central region of the image.

    Parameters:
    -----------
        output_size: tuple
            A two-tuple containing the height and width to which the image is to be cropped.

    Returns:
    --------
        PIL.Image
            Returns the cropped image.
    """

    width, height = image.size
    target_height, target_width = output_size

    top = int(round((height - target_height) / 2.0))
    left = int(round((width - target_width) / 2.0))

    return crop(image, top, left, target_height, target_width)


class AttrImage:
    """Represents a image with attributions."""

    def __init__(self, atpath):
        """
        Initializes a new AttrImage instance.

        Parameters:
        -----------
            atpath: str
                The path to the attributions.
        """

        self._atpath = atpath

    def __getitem__(self, key):
        """
        Gets the attribution with the specified key.

        Parameters:
        -----------
            key: str | range | list | tuple | numpy.ndarray
                The key of the attribution that is to be retrieved.

        Returns:
        --------
            Returns the attribution with the specified key.
        """

        if isinstance(key, slice):
            key = range(*key.indices(len(self)))

        with h5py.File(self._atpath, 'r') as fd:
            def load_index(x):
                return fd['attribution'][x].mean(0)[::-1]
            if isinstance(key, (range, list, tuple, np.ndarray)):
                return [load_index(k) for k in key]
            return load_index(key)

    def __len__(self):
        """
        Gets the number of attributions associated with the image.

        Returns:
        --------
            int
                Returns the number of attributions associated with the image.
        """

        with h5py.File(self._atpath, 'r') as fd:
            length = len(fd['attribution'])
        return length


class OrigImage:
    """Represents an original image."""

    def __init__(self, inpath):
        """
        Initializes a new OrigImage instance.

        Parameters
        ----------
            inpath: str
                The input path to a directory containing images: class_name/image_name.jpg or path to a file containing
                absolute paths to images.
        """

        self._dummy = Image.new('RGBA', (224, 224), color=(255, 0, 0, 255))
        self._fpath = inpath

        if os.path.isdir(inpath):
            self._index = sorted(glob.glob(os.path.join(inpath, '*/*')))
        else:
            with open(inpath, 'r') as f:
                self._index = sorted([x.strip() for x in f.readlines()])

    def _load_index(self, key):
        """
        Loads the image with the specified index.

        Parameters:
        -----------
            key: int
                The index of the image that is to be loaded.

        Returns:
        --------
            numpy.ndarray
                Returns the loaded image.
        """

        try:
            img = Image.open(self._index[key])
            img = center_crop(img, (224, 224))
            img = img.convert('RGB')
            img.putalpha(255)
        except FileNotFoundError:
            img = self._dummy
            LOGGER.warning('File not found, using dummy: %s', self._index[key])
        return np.array(img)[::-1]

    def __getitem__(self, key):
        """
        Gets the image at the specified index.

        Parameters:
        -----------
            key: int
                The index of the image that is to be retrieved.

        Returns:
        --------
            numpy.ndarray
                Returns the image with the specified index.
        """

        if isinstance(key, slice):
            key = range(*key.indices(len(self)))
        if isinstance(key, (range, list, tuple, np.ndarray)):
            return [self._load_index(k) for k in key]
        return self._load_index(key)
