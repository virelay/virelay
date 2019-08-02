import pytest
import numpy as np
from numpy import pi
from scipy.sparse.linalg import eigsh
import sklearn.cluster

from sprincl.processor.base import Param
from sprincl.pipeline.spectral import SpectralEmbedding, SpectralClustering
from sprincl.processor.affinity import SparseKNN
from sprincl.processor.laplacian import SymmetricNormalLaplacian
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
        se = SpectralEmbedding()
        output = se(spiral_data)
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
        sc = SpectralClustering()
        output = sc(spiral_data)
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

    def test_spectral_clustering_step_by_step_custom_params(self, spiral_data, k_knn, k_eig, k_clusters):
        # this test manually compares the pipelines working order against manually
        # executed steps with custom parameters attuned to the spiral data

        # first, separately prepare processors for customized pipeline
        # customizations:
        #   1) parameters, as passed to the test function
        #   2) all processors (affected by changed parameters) produce outputs this time for later comparison

        # let's first create a deterministic eigendecomposer and kmeans processor
        class DeterminsticEigenDecomposition(EigenDecomposition):
            # require a starting vector for the iterative eigendecomposition
            v0 = Param(dtype=np.ndarray, default=None, mandatory=True)

            def function(self, data):
                eigval, eigvec = eigsh(data, k=self.n_eigval, which=self.which, v0=self.v0)
                eigval = 1. - eigval

                if self.normalize:
                    eigvec /= np.linalg.norm(eigvec, axis=1, keepdims=True)
                return eigval, eigvec

        class DeterministicKMeans(KMeans):
            # require a starting random state for deterministic results
            random_state = Param(dtype=int, default=0, mandatory=False)

            def function(self, data):
                return sklearn.cluster.KMeans(n_clusters=self.n_clusters,
                                              random_state=self.random_state).fit_predict(data[self.index])

        knn = SparseKNN(n_neighbors=k_knn, symmetric=True, is_output=True)
        lap = SymmetricNormalLaplacian(is_output=True)
        eig = DeterminsticEigenDecomposition(n_eigval=k_eig, is_output=True,
                                             v0=np.random.randn(spiral_data.shape[0])
                                             )
        kmn = DeterministicKMeans(n_clusters=k_clusters, is_output=True, random_state=0)

        pipeline = SpectralClustering(
            affinity=knn,
            laplacian=lap,
            embedding=eig,
            clustering=kmn
        )

        output_pipeline = pipeline(spiral_data)
        assert len(output_pipeline) == 4,\
            'length of output expected to be 4 (affinity, laplacian, embedding, labels), but is {}'\
            .format(len(output_pipeline))

        # unpack pipeline results
        aff_pipe, lap_pipe, eig_pipe, label_pipe = output_pipeline

        # produce results manually and compare to pipeline output
        dist_man = pipeline.processes['pairwise_distance'](spiral_data)
        aff_man = knn(dist_man)
        np.testing.assert_array_equal(np.array(aff_man.todense()),
                                      np.array(aff_pipe.todense()),
                                      'Affinity matrices are not equal!')

        lap_man = lap(aff_man)
        np.testing.assert_array_equal(np.array(lap_man.todense()),
                                      np.array(lap_pipe.todense()),
                                      'Laplacians are not equal!')

        eig_man = eig(lap_man)
        np.testing.assert_array_equal(eig_man[0],
                                      eig_pipe[0],
                                      'Eigenvalues not equal!')
        np.testing.assert_array_equal(eig_man[1],
                                      eig_pipe[1],
                                      'Eigenvectors not equal enough!')

        label_man = kmn(eig_man[1])
        np.testing.assert_array_equal(label_man,
                                      label_pipe,
                                      'Label vectors not equal!')
