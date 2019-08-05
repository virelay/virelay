import os

import click

from sprincl import io
from sprincl.pipeline.spectral import SpectralEmbedding
from sprincl.processor.base import FunctionProcessor
from sprincl.processor.affinity import SparseKNN
from sprincl.processor.distance import SciPyPDist
from sprincl.processor.embedding import EigenDecomposition, TSNEEmbedding
from sprincl.processor.laplacian import SymmetricNormalLaplacian
from sprincl.processor.clustering import KMeans


@click.command()
@click.argument('attribution_path')
@click.argument('analysis_path')
def main(attribution_path, analysis_path):
    os.makedirs(os.path.dirname(analysis_path), exist_ok=True)
    with io.HDF5Storage(analysis_path, mode='w') as analysis_file, \
            io.HDF5Storage(attribution_path, mode='r') as attribution_file:

        analysis_file['index'] = attribution_file['index']
        pipeline = SpectralEmbedding(
            preprocessing=FunctionProcessor(function=lambda x: x.mean(1).reshape(x.shape[0], -1),
                                            bind_method=False),
            pairwise_distance=SciPyPDist(metric='euclidean'),
            affinity=SparseKNN(n_neighbors=10, symmetric=True),
            laplacian=SymmetricNormalLaplacian(),
            embedding=EigenDecomposition(n_eigval=32, io=analysis_file.at('embedding/spectral')),
        )

        eig_val, eig_vec = pipeline(attribution_file['attribution'])
        TSNEEmbedding(io=analysis_file.at('embedding/tsne'))(eig_vec)
        for n_clusters in range(2, 33):
            KMeans(n_clusters=n_clusters, io=analysis_file.at('cluster/kmeans-{}'.format(n_clusters)))(eig_vec)


if __name__ == '__main__':
    main()
