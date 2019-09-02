"""Contains some helper functions for processing images."""

import math

import numpy


def add_border(image, new_width, new_height, method):
    """
    Up-samples the specified image, by making a border around the image.

    Parameters
    ----------
        image: numpy.ndarray
            The image that is to be up-sampled.
        new_width: int
            The new width to which the image is to be up-sampled.
        new_height: int
            The new height to which the image is to be up-sampled.
        method: str
            The method that is to be used to create the border. Supported methods are 'fill_zeros' to fill up the border
            with zeros, 'fill_ones' to fill up the border with ones, 'edge_repeat' to repeat the values at the edge of
            the image, 'mirror_edge' to mirror the image at the edge, and 'wrap_around' to wrap the image around (e.g.
            the left edge is filled up with values from the right edge).

    Raises
    ------
        ValueError
            If the specified method is not supported, then a ValueError is raised

    Returns
    -------
        numpy.ndarray
            Returns the up-sampled image.
    """

    width, height, _ = image.shape
    horizontal_padding = max(0, new_width - width)
    vertical_padding = max(0, new_height - height)
    left_padding = math.ceil(float(horizontal_padding) / 2.0)
    right_padding = math.floor(float(horizontal_padding) / 2.0)
    top_padding = math.ceil(float(vertical_padding) / 2.0)
    bottom_padding = math.floor(float(vertical_padding) / 2.0)

    if method in ['fill_zeros', 'fill_ones']:
        return numpy.pad(
            image,
            ((left_padding, right_padding), (top_padding, bottom_padding), (0, 0)),
            'constant',
            constant_values=0 if method == 'zeros' else 1
        )

    internal_methods_map = {
        'edge_repeat': 'edge',
        'mirror_edge': 'reflect',
        'wrap_around': 'wrap'
    }
    if method in internal_methods_map.keys():
        return numpy.pad(
            image,
            ((left_padding, right_padding), (top_padding, bottom_padding), (0, 0)),
            internal_methods_map[method]
        )

    raise ValueError('The specified method "{0}" is not supported.'.format(method))


def center_crop(image, new_width, new_height):
    """
    Crops the image evenly on all sides to the desired size.

    Parameters
    ----------
        image: numpy.ndarray
            The image that is to be down-sampled.
        new_width: int
            The new width to which the image is to be down-sampled.
        new_height: int
            The new height to which the image is to be down-sampled.
    """

    width, height, _ = image.shape
    horizontal_crop = max(0, width - new_width)
    vertical_crop = max(0, height - new_width)
    left_crop = math.ceil(float(horizontal_crop) / 2.0)
    right_crop = math.floor(float(horizontal_crop) / 2.0)
    top_crop = math.ceil(float(vertical_crop) / 2.0)
    bottom_crop = math.floor(float(vertical_crop) / 2.0)

    return image[left_crop:new_width + right_crop, top_crop:new_height + bottom_crop, :]
