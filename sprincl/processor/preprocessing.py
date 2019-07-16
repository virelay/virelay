import numpy as np

from .base import Processor

class PreProcessor(Processor):
    """Base-class for preprocessing.

    """
    pass

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

