import pytest
import numpy as np
from numpy import pi


import os
import matplotlib.pyplot as plt

from sprincl.pipeline.spectral import SpectralEmbedding, SpectralClustering
from sprincl.processor.affinity import SparseKNN
from sprincl.processor.laplacian import SymmetricNormalLaplacian
from sprincl.processor.embedding import EigenDecomposition
from sprincl.processor.clustering import KMeans



import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy import sparse as sp
from scipy.sparse.linalg import eigsh
from sklearn.cluster import KMeans as SKKMeans
from sklearn.manifold import TSNE
from sklearn import datasets
from sklearn.decomposition import PCA

def knn_fn(distance, k, symmetric):
    """Compute Sparse K-Nearest-Neighbors affinity matrix.

    Parameters
    ----------
    distance : :obj:`numpy.ndarray`
        Distance matrix used to compute affinity matrix.

    Returns
    ------
    :obj:`sp.csr_matrix`
        Sparse CSR representation of KNN affinity matrix

    """
    # number of samples
    n = distance.shape[0]

    # silently use maximum number of neighbors if there are more samples than k
    k = k if k < (n-1) else (n-1)

    # set up indices for sparse representation of nearest neighbors
    cols = distance.argsort(1)[:, 1:k+1]
    rows = np.mgrid[:n, :k][0]
    # existing edges are denoted with ones
    vals = np.ones((n, k), dtype=distance.dtype)
    affinity = sp.csr_matrix((vals.flat, (rows.flat, cols.flat)), shape=(n, n))

    # make the affinity matrix symmetric
    if symmetric:
        affinity = (affinity + affinity.T) / 2.
    return affinity


def laplacian(affinity):
    def A1ifmat(x):
        return x.A1 if isinstance(x, np.matrix) else x
    deg = sp.diags(A1ifmat(affinity.sum(1))**-.5, 0)
    lap = deg @ affinity @ deg
    return lap


def completely_manual_pipeline(data, k_knn, k_eig, k_clusters, v0=None, random_state=None):
    D = squareform(pdist(data))

    A = knn_fn(D, k=k_knn, symmetric=True)
    L = laplacian(A)

    eigval, eigvec = eigsh(L, k=k_eig, which='LM', v0=v0)
    eigval = 1. - eigval
    eigvec /= np.linalg.norm(eigvec, axis=1, keepdims=True)

    labels = SKKMeans(n_clusters=k_clusters).fit_predict(eigvec)

    return {'A':A, 'D':D, 'L':L, 'eigval':eigval, 'eigvec':eigvec, 'labels':labels, 'data':data}

@pytest.fixture(scope='module')
def spiral_data(N=150):      # N = samples per class of the two classes
    np.random.seed(1345123)  # fix seed for data
    _ = np.random.uniform(size=(2, 100)).T  # "part of the seed"

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

        knn = SparseKNN(n_neighbors=k_knn, symmetric=True, is_output=True)
        lap = SymmetricNormalLaplacian(is_output=True)

        v0 = np.random.rand(spiral_data.shape[0]) # some fixed init vector
        v0 /= np.linalg.norm(v0,1)
        eig = EigenDecomposition(n_eigval=k_eig, is_output=True,
                                 kwargs={'v0': v0})

        random_state = 0
        kmn = KMeans(n_clusters=k_clusters, is_output=True,
                     kwargs={'random_state': random_state})

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

        path = '/tmp/spectral_eigenvalues.pdf'
        plt.figure()
        plt.plot(eig_pipe[0][::-1], '.')
        plt.xticks([])
        plt.yticks([])
        plt.savefig(path)
        # os.remove(path)

        path = '/tmp/spectral_labelling.pdf'
        plt.figure()
        plt.scatter(x=spiral_data[:, 0], y=spiral_data[:, 1], c=label_pipe)
        plt.xticks([])
        plt.yticks([])
        plt.savefig(path)
        # os.remove(path)




        # testing against completely manual implementation of pipeline
        results = completely_manual_pipeline(spiral_data, k_knn, k_eig, k_clusters, v0=v0, random_state=random_state)

        path = '/tmp/spectral_labelling_manual.pdf'
        plt.figure()
        plt.scatter(x=results['data'][:,0], y=results['data'][:,1], c=results['labels'])
        plt.xticks([])
        plt.yticks([])
        plt.savefig(path)

        # this is fine so far.
        np.testing.assert_array_equal(dist_man,
                                    results['D'],
                                    'Manual and completely manual distance not equal!'
                                    )

        # also this is fine so far.
        np.testing.assert_array_equal(np.array(aff_man.todense()),
                                      np.array(results['A'].todense()),
                                      'Manual and completely manual affinity matrices are not equal!')

        # also this is fine so far.
        np.testing.assert_array_equal(np.array(lap_man.todense()),
                                      np.array(results['L'].todense()),
                                      'Manual and completely manual Laplacians are not equal!')

        # also this is fine so far, WHEN THE INITIAL V0 IS PASSED. IS THIS THE SOURCE FOR THE WRONG LABELS?
        np.testing.assert_array_equal(eig_man[0],
                                      results['eigval'],
                                      'Manual and completely manual Eigenvalues not equal!')




