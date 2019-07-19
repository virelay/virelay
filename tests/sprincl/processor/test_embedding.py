import pytest
from sklearn.datasets import load_digits
from sklearn.metrics.pairwise import euclidean_distances

from sprincl.processor import embedding


@pytest.fixture
def data():
    digits = load_digits()  # shape 1797 x 64
    return digits.data


@pytest.fixture
def distances(data):
    return euclidean_distances(data)


@pytest.mark.parametrize('processor', [embedding.TSNEEmbedding, embedding.LLEEmbedding, embedding.PCAEmbedding,
                                       embedding.UMAPEmbedding])
def test_embedding(processor, data):
    emb = processor()(data)
    assert emb.shape == (1797, 2)


def test_eigen_decomposition(distances):
    eigval, eigvec = embedding.EigenDecomposition(n_eigval=32)(distances)
    assert eigval.shape == (32, )
    assert eigvec.shape == (1797, 32)


@pytest.mark.parametrize('processor', [embedding.TSNEEmbedding, embedding.LLEEmbedding, embedding.PCAEmbedding,
                                       embedding.UMAPEmbedding])
def test_embedding_on_distances(processor, distances):
    emb = processor(metric='precomputed')(distances)
    assert emb.shape == (1797, 2)
