"""Preprocessing Processors

"""
from types import FunctionType

import numpy as np
import skimage.transform
import skimage.measure

from .base import Processor, Param


class PreProcessor(Processor):
    """Base-class for preprocessing.

    """
    kwargs = Param(dict, {})


class Histogram(PreProcessor):
    """Channel-wise histograms of data

    Parameters
    ----------
    bins : int
        number of bins for histograms

    """
    bins = Param(int, 32)

    def function(self, data):
        """Compute channel-wise histograms from data

        Parameters
        ----------
        data : :obj:`numpy.ndarray`
            image data with shape samples x channels x height x width

        Returns
        -------
        :obj:`numpy.ndarray`
            Channel-wise histograms with shape samples x channels x bins

        """
        n, c, h, w = data.shape
        # channel-wise range
        trange = zip(data.min((0, 2, 3), data.max(0, 2, 3)))
        hist = np.histogramdd(data.reshape(n * c, h * w),
                              bins=self.bins, range=trange, density=True).reshape(n, c, self._bins)
        return hist


class ImagePreProcessor(PreProcessor):
    """
    Parameters
    ----------
    filter : int
        The order of interpolation. The order has to be in the range 0-5:
         - 0: Nearest-neighbor
         - 1: Bi-linear (default)
         - 2: Bi-quadratic
         - 3: Bi-cubic
         - 4: Bi-quartic
         - 5: Bi-quintic
    channels_first: bool
        True if channels first else False.
    """
    filter = Param(int, 1)
    channels_first = Param(bool, True)


class Resize(ImagePreProcessor):
    """Resize images.

    Parameters
    ----------
    width : int
        Width of resized images. Default: 100
    height: int
        Height of resized images. Default: 100
    filter : int
        The order of interpolation. The order has to be in the range 0-5:
         - 0: Nearest-neighbor
         - 1: Bi-linear (default)
         - 2: Bi-quadratic
         - 3: Bi-cubic
         - 4: Bi-quartic
         - 5: Bi-quintic
    channels_first: bool
        True if channels first else False.
    kwargs: dict
        Check skimage.transform.resize.

    """
    width = Param(int, 100)
    height = Param(int, 100)

    def function(self, data):
        return np.stack(skimage.transform.resize(x, output_shape=(self.height, self.width), order=self.filter,
                                                 **self.kwargs)
                        for x in data)


class Rescale(ImagePreProcessor):
    """Rescale images.

    Parameters
    ----------
    scale : float
        Scale to which the images are rescaled. Default: 0.5
    filter : int
        The order of interpolation. The order has to be in the range 0-5:
         - 0: Nearest-neighbor
         - 1: Bi-linear (default)
         - 2: Bi-quadratic
         - 3: Bi-cubic
         - 4: Bi-quartic
         - 5: Bi-quintic
    channels_first: bool
        True if channels first else False.
    kwargs: dict
        Check skimage.transform.rescale.

    """
    scale = Param(float, 0.5)

    def function(self, data):
        return np.stack(skimage.transform.rescale(x, self.scale, order=self.filter, **self.kwargs) for x in data)


class Pooling(PreProcessor):
    """Preform pooling operation on given stride.

    Parameters
    ----------
    stride : tuple[float]
        The pooling stride. Default: (batch, channel, height, width) -> (1, 1, 2, 2)
    pooling_function: FunctionType
        Function that reduces the selected blocks. Default: np.sum
    kwargs: dict
        Check skimage.measure.block_reduce.

    """
    stride = Param(tuple, (1, 1, 2, 2))
    pooling_function = Param(FunctionType, np.sum)

    def function(self, data):
        return skimage.measure.block_reduce(data, self.stride, self.pooling_function, **self.kwargs)
