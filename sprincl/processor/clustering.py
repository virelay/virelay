import logging

import numpy as np
from sklearn.cluster import KMeans

from .base import Processor

logger = logging.getLogger(__name__)

class Clustering(Processor):
    """Clustering Processor

    """
    pass

class KMeans(Clustering):
    """KMeans Clustering

    """
    n_cluster = Param(int, 2)

    def function(self, data):
        return KMeans(n_clusters=self.n_cluster).fit_predict(data)

