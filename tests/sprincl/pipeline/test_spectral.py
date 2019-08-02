import pytest
import numpy as np
from numpy import pi
# from scipy import sparse as sp

# from scipy.spatial.distance import pdist, squareform
# from scipy.sparse.linalg import eigsh
# from sklearn.cluster import KMeans
# from sklearn.manifold import TSNE

from sprincl.processor.base import Processor
from sprincl.pipeline.base import Task
from sprincl.pipeline.spectral import SpectralEmbedding, SpectralClustering

from sprincl.processor.affinity import SparseKNN
from sprinc.processor.laplacian import SymmetricNormalLaplacian
from sprincl.processor.embedding import EigenDecomposition
from sprincl.processor.clustering import KMeans


@pytest.fixture(scope='module')
def spiral_data(N=150):      # N = samples per class of the two classes
    np.random.seed(1345123)  # fix seed for data

    # generates double-spiral data in 2-d with N data points
    theta = np.sqrt(np.random.rand(N)) * 2 * pi

    r_a = 2 * theta + pi
    data_a = np.array([np.cos(theta) * r_a, np.sin(theta) * r_a]).T
    x_a = data_a + np.random.randn(N, 2) * .5

    r_b = -2 * theta - pi
    data_b = np.array([np.cos(theta) * r_b, np.sin(theta) * r_b]).T
    x_b = data_b + np.random.randn(N, 2) * .5

    return np.append(x_a, x_b, axis=0)


@pytest.fixture(scope='module')
def k_knn(spiral_data):
    return int(np.log(spiral_data.shape[0]))


@pytest.fixture(scope='module')
def k_eig():
    return 8


@pytest.fixture(scope='module')
def k_clusters():
    return 4


class TestSpectral(object):

    def test_spectral_embedding_instatiation(self):
        # test whether we can instantiate a spectral embedding instance successfully
        SpectralEmbedding()

    def test_spectral_clustering_instatiation(self):
        # test whether we can instantiate a spectral clustering instance successfully
        SpectralClustering()

    def test_data_generation(self, spiral_data):
        # sanity check. make sure the data looks as expected (from the outside)
        assert isinstance(spiral_data, np.ndarray), 'Expected numpy.ndarray type, got {}'.format(type(spiral_data))
        assert spiral_data.shape == (300, 2), 'Expected spiral_data shape (300, 2), got {}'.format(spiral_data.shape)

    def test_spectral_embedding_default_params(self, spiral_data):
        # test wheter the SE operates on data all the way through, using its default parameters.
        SE = SpectralEmbedding()
        output = SE(spiral_data)
        assert isinstance(output, tuple), 'Expected tuple type output, got {}'.format(type(output))
        assert len(output) == 2, 'Expected output length of 2, got {}'.format(len(output))

        eigval, eigvec = output
        assert isinstance(eigval, np.ndarray), 'Expected eigval to be numpy.ndarray, but got {}'.format(type(eigval))
        assert isinstance(eigvec, np.ndarray), 'Expected eigvec to be numpy.ndarray, but got {}'.format(type(eigvec))
        assert eigvec.shape[0] == spiral_data.shape[0],\
            'Expected number of eigenvectors to be identical to number of samples ({}), but got {}'\
            .format(spiral_data.shape[0], eigvec.shape[0])
        assert eigvec.shape[1] == eigval.size,\
            'Expected dim of eigenvectors {} be be identical to the number of reported eigenvalues {}'\
            .format(eigvec.shape[1], eigval.size)

    def test_spectral_clustering_default_params(self, spiral_data):
        # test wheter the SC operates on data all the way through, using its default parameters.
        SC = SpectralClustering()
        output = SC(spiral_data)
        assert isinstance(output, tuple), 'Expected tuple type output, got {}'.format(type(output))
        assert len(output) == 2, 'Expected output lenght of 2, got {}'.format(len(output))

        eigenstuff, labels = output
        assert isinstance(eigenstuff, tuple),\
            'Expected tuple type output for eigenstuff, got {}'.format(type(eigenstuff))
        assert len(eigenstuff) == 2,\
            'Expected eigenstuff length of 2, got {}'.format(len(eigenstuff))

        eigval, eigvec = eigenstuff
        assert isinstance(eigval, np.ndarray), 'Expected eigval to be numpy.ndarray, but got {}'.format(type(eigval))
        assert isinstance(eigvec, np.ndarray), 'Expected eigvec to be numpy.ndarray, but got {}'.format(type(eigvec))
        assert eigvec.shape[0] == spiral_data.shape[0],\
            'Expected number of eigenvectors to be identical to number of samples ({}), but got {}'\
            .format(spiral_data.shape[0], eigvec.shape[0])
        assert eigvec.shape[1] == eigval.size,\
            'Expected dim of eigenvectors {} be be identical to the number of reported eigenvalues {}'\
            .format(eigvec.shape[1], eigval.size)

        assert isinstance(labels, np.ndarray), 'Expected labels to be numpy.ndarray, but got {}'.format(type(labels))
        assert labels.size == spiral_data.shape[0],\
            'Expected number of labels to be identical to number of samples in spiral_data ({}), but got {}'\
            .format(spiral_data.shape[0], labels.size)

        assert labels.ndim == 1, 'Expected labels to be flat array, but was shaped {}'.format(labels.shape)
