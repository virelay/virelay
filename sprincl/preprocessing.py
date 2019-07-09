import numpy as np

class Preprocessor(object):
    """Base-class for preprocessing.

    """
    def __call__(self, data):
        raise NotImplementedError

    def __add__(self, other):
        assert isinstance(other, __class__)
        return (lambda x: self(other(x)))

class Histogram(Preprocessor):
    """Channel-wise histograms of data

    """
    def __init__(self, *args, bins=32, **kwargs):
        """Initialize Histogram Preprocessor

        Parameters
        ----------
        bins : int
            number of bins for histograms

        """
        self._bins = bins

    def __call__(self, data):
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
                              bins=self._bins, range=trange, density=True).reshape(n, c, self._bins)
        return hist

