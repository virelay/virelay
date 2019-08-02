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



    def test_spectral_clustering_step_by_step_custom_params(self, spiral_data, k_knn, k_eig, k_clusters):
        # this test manually compares the pipelines working order against manually
        # executed steps with custom parameters attuned to the spiral data

        # first, separately prepare processors for customized pipeline
        # customizations:
        #   1) parameters, as passed to the test function
        #   2) all processors (affected by changed parameters) produce outputs this time for later comparison
        knn = SparseKNN(k_neighbors=k_knn, symmetric=True, is_output=True)
        lap = #CONTINUE HERE: 1) BACKUP THIS CODE; GO TO / FAST FORWARD MASTER / CONTINUE WRITING TEST CODE.

        assert isinstance(knn, Processor), 'YAY'
        pipeline = SpectralClustering(
            affinity=knn,

        )

        output = pipeline(spiral_data)
        assert len(output) == 2, 'len output is {}'.format(len(output))


        # WEIRDNESS BELOW!

        # pipeline = SpectralClustering(
        #    affinity=SparseKNN(k_neighbors=k_knn, symmetric=True),
        #    embedding=EigenDecomposition(n_eigval=k_eig),
        #    clustering=KMeans(n_clusters=k_clusters) # WORKS!
        # )

        # pipeline = SpectralClustering(
        #     affinity=Task(default=SparseKNN(k_neighbors=k_knn, symmetric=True)), #<- change!
        #     embedding=EigenDecomposition(n_eigval=k_eig),
        #     clustering=KMeans(n_clusters=k_clusters) #fails because of this!
        # )



        # def test_assert_with_spiral_data(self):
        #     # this test tries to run/assert the results of the Pipeline implementation with a manual pipeline.


        #     from sprincl.pipeline.spectral import SpectralClustering



        #     def knn(distance, k, symmetric):
        #         """Compute Sparse K-Nearest-Neighbors affinity matrix.
        #         Note: This is the old KNN code from previous sprincl versions

        #         Parameters
        #         ----------
        #         distance : :obj:`numpy.ndarray`
        #             Distance matrix used to compute affinity matrix.

        #         Returns
        #         ------
        #         :obj:`sp.csr_matrix`
        #             Sparse CSR representation of KNN affinity matrix

        #         """
        #         # number of samples
        #         n = distance.shape[0]

        #         # silently use maximum number of neighbors if there are more samples than k
        #         k = k if k < (n-1) else (n-1)

        #         # set up indices for sparse representation of nearest neighbors
        #         cols = distance.argsort(1)[:, 1:k+1]
        #         rows = np.mgrid[:n, :k][0]
        #         # existing edges are denoted with ones
        #         vals = np.ones((n, k), dtype=distance.dtype)
        #         affinity = sp.csr_matrix((vals.flat, (rows.flat, cols.flat)), shape=(n, n))

        #         # make the affinity matrix symmetric
        #         if symmetric:
        #             affinity = (affinity + affinity.T) / 2.
        #         return affinity

        #     def laplacian(affinity):
        #         """ Note: this is the old laplacian code from a previous sprincl version """
        #         def A1ifmat(x):
        #             return x.A1 if isinstance(x, np.matrix) else x
        #         deg = sp.diags(A1ifmat(affinity.sum(1))**-.5, 0)
        #         lap = deg @ affinity @ deg
        #         return lap

        #     #generate some data
        #     np.random.seed(1345123)
        #     data = spiral_data(150)

        #     #run the manual pipeline
        #     k_knn = int(np.log(data.shape[0]))
        #     k_eig = 8
        #     k_clusters = 4

        #     D_man = squareform(pdist(data))
        #     A_man = knn(D_man, k=k_knn, symmetric=True)
        #     L_man = laplacian(A_man)

        #     eigval_man, eigvec_man = eigsh(L_man, k=k_eig, which='LM')
        #     eigval_man = 1. - eigval_man
        #     eigvec_man /= np.linalg.norm(eigvec_man, axis=1, keepdims=True)
        #     labels_man = KMeans(n_clusters=k_clusters).fit_predict(eigvec_man)
        #     e_data_man = TSNE().fit_transform(eigvec_man)   #compute embedding for Data

        #     # build the SpRAy pipeline

        #     SC = SpectralClustering
        #     labels_pipe = SC(data)
        #     print(labels_pipe)
