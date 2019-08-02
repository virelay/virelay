import os

from sprincl import io
from sprincl.pipeline.spectral import SpectralClustering
from sprincl.processor.base import FunctionProcessor
from sprincl.processor.affinity import SparseKNN
from sprincl.processor.distance import SciPyPDist
from sprincl.processor.embedding import EigenDecomposition
from sprincl.processor.laplacian import SymmetricNormalLaplacian
from sprincl.processor.clustering import KMeans


# Processors
attribution_path = '/home/marinc/sprincl/attribution/PascalVOC2007/' \
                   'bvcl_caffenet_multilabel-lrp_composite+flat-horse_true.input.h5'
analysis_path = '/home/marinc/sprincl/analysis/PascalVOC2007/test.h5'

os.makedirs(os.path.dirname(analysis_path), exist_ok=True)

with io.HDF5Storage(analysis_path, mode='w') as analysis_file, \
        io.HDF5Storage(attribution_path, mode='r') as attribution_file:

    analysis_file['index'] = attribution_file['index']
    pipeline = SpectralClustering(
        preprocessing=FunctionProcessor(function=lambda x: x.mean(1).reshape(x.shape[0], -1),
                                        bind_method=False),
        pairwise_distance=SciPyPDist(metric='euclidean'),
        affinity=SparseKNN(n_neighbors=10, symmetric=True),
        laplacian=SymmetricNormalLaplacian(),
        embedding=EigenDecomposition(n_eigval=32, io=analysis_file.at('embedding/spectral')),
        clustering=KMeans(n_clusters=2, io=analysis_file.at('cluster/kmeans-2'))
    )

    output = pipeline(attribution_file['attribution'])
