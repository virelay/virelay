import os

import pytest
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics.pairwise import euclidean_distances

from sprincl.processor import clustering

try:
    import hdbscan  # noqa: F401
    extra_processors = [clustering.HDBSCAN]
except ImportError:
    extra_processors = []


@pytest.fixture
def data():
    data, _ = make_blobs(1000, centers=5, random_state=100)
    return data


@pytest.fixture
def tiny_data():
    data, _ = make_blobs(50, centers=5, random_state=100)
    return data


@pytest.fixture
def distances(data):
    return euclidean_distances(data)


@pytest.mark.parametrize('processor', [clustering.AgglomerativeClustering, clustering.KMeans])
def test_clustering(processor, data):
    emb = processor(n_clusters=5)(data)
    # since blobs are equal the cluster sizes should be approximately the same size
    assert len(np.unique(emb)) == 5
    assert (np.unique(emb, return_counts=True)[1] / 1000).std() < 0.05


@pytest.mark.parametrize('processor', [clustering.DBSCAN] + extra_processors)
def test_embedding_on_distances(processor, distances):
    params = {'eps': 0.9} if 'eps' in processor.params else {}
    emb = processor(metric='precomputed', **params)(distances)
    assert len(np.unique(emb)) == 5
    assert (np.unique(emb, return_counts=True)[1] / 1000).std() < 0.13


def test_embedding_on_distances_agg_clustering(distances):
    emb = clustering.AgglomerativeClustering(n_clusters=5, metric='precomputed', linkage='average')(distances)
    assert (np.unique(emb, return_counts=True)[1] / 1000).std() < 0.05


def test_denrogram_creation(tiny_data):
    output_path = '/tmp/dendrogram.png'
    data2 = clustering.Dendrogram(output_file=output_path)(tiny_data)
    np.testing.assert_equal(tiny_data, data2)
    assert os.path.exists(output_path)
    os.remove(output_path)


def test_denrogram_creation_with_file_object(tiny_data):
    output_path = '/tmp/dendrogram.png'
    with open(output_path, 'wb') as f:
        data2 = clustering.Dendrogram(output_file=f)(tiny_data)
        np.testing.assert_equal(tiny_data, data2)
        assert os.path.exists(output_path)
    os.remove(output_path)
