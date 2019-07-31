import pytest
from sklearn.datasets import load_digits
from sklearn.metrics.pairwise import euclidean_distances

from sprincl.processor import embedding

embedding_processors = [embedding.TSNEEmbedding, embedding.LLEEmbedding, embedding.PCAEmbedding]

try:
    import umap  # noqa: F401
    extra_processors = [embedding.UMAPEmbedding]
except ImportError:
    extra_processors = []


@pytest.fixture
def data():
    digits = load_digits(2)  # shape 1797 x 64
    return digits.data


@pytest.fixture
def distances(data):
    return euclidean_distances(data)


@pytest.mark.parametrize('processor', embedding_processors + extra_processors)
def test_embedding(processor, data):
    emb = processor()(data)
    assert emb.shape == (360, 2)


def test_eigen_decomposition(distances):
    eigval, eigvec = embedding.EigenDecomposition(n_eigval=32)(distances)
    assert eigval.shape == (32, )
    assert eigvec.shape == (360, 32)


@pytest.mark.parametrize('processor', [embedding.TSNEEmbedding] + extra_processors)
def test_embedding_on_distances(processor, distances):
    emb = processor(metric='precomputed')(distances)
    assert emb.shape == (360, 2)
