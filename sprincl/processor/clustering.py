import os
import logging

import numpy as np
from sklearn import cluster
from matplotlib import pyplot as plt
import scipy.cluster.hierarchy as shc

from .base import Processor, Param


try:
    import hdbscan
except ImportError:
    class hdbscan(object):
        def __getattr__(self, item):
            raise RuntimeError("Support for hdbscan was not installed!")
    hdbscan = hdbscan()


LOGGER = logging.getLogger(__name__)


class Clustering(Processor):
    """Clustering Processor

    """
    kwargs = Param(dict, default={})


class KMeans(Clustering):
    """KMeans Clustering

    """
    n_clusters = Param(int, 2)
    index = Param(tuple, (slice(None),))

    def function(self, data):
        return cluster.KMeans(n_clusters=self.n_clusters, **self.kwargs).fit_predict(data[self.index])


class HDBSCAN(Clustering):
    """HDBSCAN clustering:  https://github.com/scikit-learn-contrib/hdbscan

    """
    __doc__ = hdbscan.HDBSCAN.__doc__
    n_clusters = Param(int, 5)
    metric = Param(str, 'euclidean')

    def function(self, data):
        clustering = hdbscan.HDBSCAN(min_cluster_size=self.n_clusters, metric=self.metric, **self.kwargs)
        return clustering.fit_predict(data)


class DBSCAN(Clustering):
    __doc__ = cluster.DBSCAN.__doc__
    metric = Param(str, 'euclidean')
    eps = Param(float, 0.5)
    min_samples = Param(int, 5)

    def function(self, data):
        clustering = cluster.DBSCAN(eps=self.eps, min_samples=self.min_samples, metric=self.metric, **self.kwargs)
        return clustering.fit_predict(data)


class AgglomerativeClustering(Clustering):
    __doc__ = cluster.AgglomerativeClustering.__doc__
    n_clusters = Param(int, 5)
    metric = Param(str, 'euclidean')
    linkage = Param(str, 'ward')

    def function(self, data):
        clustering = cluster.AgglomerativeClustering(n_clusters=self.n_clusters, affinity=self.metric,
                                                     linkage=self.linkage, **self.kwargs)
        return clustering.fit_predict(data)


class Dendrogram(Clustering):
    """Dendrogram

    """
    output_path = Param(str, '/tmp/dendrogram.png')
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
