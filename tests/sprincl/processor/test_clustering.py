import os

import pytest
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics.pairwise import euclidean_distances

from sprincl.processor import clustering


@pytest.fixture
def data():
    data, _ = make_blobs(1000, centers=5, random_state=100)
    return data


@pytest.fixture
def distances(data):
    return euclidean_distances(data)


@pytest.mark.parametrize('processor', [clustering.KMeans, clustering.AgglomerativeClustering, clustering.DBSCAN,
                                       clustering.HDBSCAN])
def test_clustering(processor, data):
    # TODO DBSCAN and HDBSCAN are failing this test, not sure how to use them
    emb = processor(n_clusters=5)(data)
    # since blobs are equal the cluster sizes should be approximately the same size
    assert (np.unique(emb, return_counts=True)[1] / 1000).std() < 0.05


@pytest.mark.parametrize('processor', [clustering.KMeans, clustering.DBSCAN, clustering.HDBSCAN])
def test_embedding_on_distances(processor, distances):
    # TODO DBSCAN, HDBSCAN are failing this test. Any suggestions?
    emb = processor(n_clusters=5, metric='precomputed')(distances)
    assert (np.unique(emb, return_counts=True)[1] / 1000).std() < 0.05


def test_embedding_on_distances_agg_clustering(distances):
    emb = clustering.AgglomerativeClustering(n_clusters=5, metric='precomputed', linkage='average')(distances)
    assert (np.unique(emb, return_counts=True)[1] / 1000).std() < 0.05


def test_denrogram_creation(data):
    output_path = '/tmp/dendrogram.png'
    data2 = clustering.Dendrogram(output_file=output_path)(data)
    np.testing.assert_equal(data, data2)
    assert os.path.exists(output_path)
    os.remove(output_path)


def test_denrogram_creation_with_file_object(data):
    output_path = '/tmp/dendrogram.png'
    with open(output_path, 'wb') as f:
        data2 = clustering.Dendrogram(output_file=f)(data)
        np.testing.assert_equal(data, data2)
        assert os.path.exists(output_path)
    os.remove(output_path)
