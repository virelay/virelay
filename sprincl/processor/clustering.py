"""Clustering Processors

"""
import logging

from sklearn.cluster import KMeans as SK_KMeans

from .base import Processor, Param

logger = logging.getLogger(__name__)


class Clustering(Processor):
    """Clustering Processor

    """


class KMeans(Clustering):
    """KMeans Clustering

    """
    n_cluster = Param(int, 2)
    index = Param(tuple, (slice(None),))

    def function(self, data):
        return SK_KMeans(n_clusters=self.n_cluster).fit_predict(data[self.index])
