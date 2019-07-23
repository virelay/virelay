import os
import logging

import numpy as np
import sklearn.cluster
from matplotlib import pyplot as plt
import scipy.cluster.hierarchy as shc

from .base import Processor, Param


try:
    import hdbscan
except ImportError:
    class hdbscan(object):
        def __getattr__(self, item):
            raise RuntimeError("Support for hdbscan was not installed! Install with: pip install {}[{}]".format(
                __name__.split('.')[0], "hdbscan"))
    hdbscan = hdbscan()


LOGGER = logging.getLogger(__name__)


class Clustering(Processor):
    """Clustering Processor

    """
    kwargs = Param(dict, default={})


class KMeans(Clustering):
    """KMeans Clustering

    Parameters
    ----------
    n_clusters: int
        Default: 2
    index: tuple
        Default: empty slice
    kwargs: dict
        See also: :obj:`sklearn.cluster.KMeans`

    See Also
    --------
    :obj:`sklearn.cluster.KMeans`

    """
    n_clusters = Param(int, 2)
    index = Param(tuple, (slice(None),))

    def function(self, data):
        return sklearn.cluster.KMeans(n_clusters=self.n_clusters, **self.kwargs).fit_predict(data[self.index])


class HDBSCAN(Clustering):
    """HDBSCAN clustering

    Parameters
    ----------
    n_clusters: int
        Default: 2
    metric: str
        Default: euclidean
    kwargs: dict
        See also: :obj:`hdbscan.HDBSCAN`

    See Also
    --------
    :obj:`hdbscan.HDBSCAN`

    Notes
    -----
    https://github.com/scikit-learn-contrib/hdbscan

    """
    n_clusters = Param(int, 5)
    metric = Param(str, 'euclidean')

    def function(self, data):
        clustering = hdbscan.HDBSCAN(min_cluster_size=self.n_clusters, metric=self.metric, **self.kwargs)
        return clustering.fit_predict(data)


class DBSCAN(Clustering):
    """DBSCAN clustering

    Parameters
    ----------
    metric: str
        Default: euclidean
    eps: float
        Default: 0.5
    min_samples: int
        Default: 5
    kwargs: dict
        See also: :obj:`sklearn.cluster.DBSCAN`

    See Also
    --------
    :obj:`sklearn.cluster.DBSCAN`

    """
    metric = Param(str, 'euclidean')
    eps = Param(float, 0.5)
    min_samples = Param(int, 5)

    def function(self, data):
        clustering = sklearn.cluster.DBSCAN(eps=self.eps, min_samples=self.min_samples, metric=self.metric,
                                            **self.kwargs)
        return clustering.fit_predict(data)


class AgglomerativeClustering(Clustering):
    """Agglomerative clustering

    Parameters
    ----------
    n_clusters: int
        Default: 5
    metric: str
        Options: "euclidean", "l1", "l2", "manhattan", "cosine", or 'precomputed'. Default: "euclidean"
    linkage: str
        Options: "ward", "complete", "average", "single". Default: "ward"
    kwargs: dict
        See also: :obj:`sklearn.cluster.AgglomerativeClustering`

    See Also
    --------
    :obj:`sklearn.cluster.AgglomerativeClustering`

    """
    n_clusters = Param(int, 5)
    metric = Param(str, 'euclidean')
    linkage = Param(str, 'ward')

    def function(self, data):
        clustering = sklearn.cluster.AgglomerativeClustering(n_clusters=self.n_clusters, affinity=self.metric,
                                                             linkage=self.linkage, **self.kwargs)
        return clustering.fit_predict(data)


class Dendrogram(Clustering):
    """Dendrogram

    Parameters
    ----------
    output_path: str
        Path to where the dendrogram is saved,
    metric: str
        Options: "euclidean", "l1", "l2", "manhattan", "cosine", or 'precomputed'. Default: "euclidean"
    linkage: str
        Options: "ward", "complete", "average", "single". Default: "ward"

    """
    output_path = Param(str)
    metric = Param(str, 'euclidean')
    linkage = Param(str, 'ward')

    def function(self, data):
        """Saves Dendrogram by default to /tmp/dendrogram.png and returns the input data.

        """
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        plt.figure(figsize=(10, 7))
        shc.dendrogram(shc.linkage(data, method=self.linkage))
        plt.savefig(self.output_path)
        return data
