"""Performs a meta-analysis on an attribution database and writes them into an analysis database, from which a ViRelAy
project can be created.
"""

import json
import argparse
from typing import List

import h5py
import numpy

from corelay.base import Param
from corelay.processor.base import Processor
from corelay.processor.affinity import SparseKNN
from corelay.processor.distance import SciPyPDist
from corelay.processor.flow import Sequential, Parallel
from corelay.pipeline.spectral import SpectralClustering
from corelay.processor.embedding import TSNEEmbedding, UMAPEmbedding, EigenDecomposition
from corelay.processor.clustering import KMeans, DBSCAN, HDBSCAN, AgglomerativeClustering


class Flatten(Processor):
    """Represents a CoRelAy processor, which flattens its input data."""

    def function(self, data: numpy.ndarray) -> numpy.ndarray:
        """Applies the flattening to the input data.

        Parameters
        ----------
            data: numpy.ndarray
                The input data that is to be flattened.

        Returns
        -------
            numpy.ndarray
                Returns the flattened data.
        """

        return data.reshape(data.shape[0], numpy.prod(data.shape[1:]))


class SumChannel(Processor):
    """Represents a CoRelAy processor, which sums its input data across channels, i.e., its second axis."""

    def function(self, data: numpy.ndarray) -> numpy.ndarray:
        """Applies the summation over the channels to the input data.

        Parameters
        ----------
            data: numpy.ndarray
                The input data that is to be summed over its channels.

        Returns
        -------
            numpy.ndarray
                Returns the data that was summed up over its channels.
        """

        return data.sum(axis=1)


class Absolute(Processor):
    """Represents a CoRelAy processor, which computes the absolute value of its input data."""

    def function(self, data: numpy.ndarray) -> numpy.ndarray:
        """Computes the absolute value of the specified input data.

        Parameters
        ----------
            data: numpy.ndarray
                The input data for which the absolute value is to be computed.

        Returns
        -------
            numpy.ndarray
                Returns the absolute value of the input data.
        """

        return numpy.absolute(data)


class Normalize(Processor):
    """Represents a CoRelAy processor, which normalizes its input data.

    Attributes
    ----------
        axes: Param
            A parameter of the processor, which determines the axis over which the data is to be normalized. Defaults to
            the second and third axes.
    """

    axes = Param(tuple, (1, 2))

    def function(self, data: numpy.ndarray) -> numpy.ndarray:
        """Normalizes the specified input data.

        Parameters
        ----------
            data: numpy.ndarray
                The input data that is to be normalized.

        Returns
        -------
            numpy.ndarray
                Returns the normalized input data.
        """

        return data / data.sum(self.axes, keepdims=True)


class Histogram(Processor):
    """Represents a CoRelAy processor, which computes a histogram over its input data.

    Attributes
    ----------
        bins: Param
            A parameter of the processor, which determines the number of bins that are used to compute the histogram.
    """

    bins = Param(int, 256)

    def function(self, data: numpy.ndarray) -> numpy.ndarray:
        """Computes histograms over the specified input data. One histogram is computed for each channel and each sample
        in a batch of input data.

        Parameters
        ----------
            data: numpy.ndarray
                The input data over which the histograms are to be computed.

        Returns
        -------
            numpy.ndarray
                Returns the histograms that were computed over the input data.
        """

        return numpy.stack([
            numpy.stack([
                numpy.histogram(
                    sample.reshape(sample.shape[0], numpy.prod(sample.shape[1:3])),
                    bins=self.bins,
                    density=True
                ) for sample in channel
            ]) for channel in data.transpose(3, 0, 1, 2)])


# Contains the various pre-processing method and distance metric variants that can be used to compute the analysis
VARIANTS = {
    'absspectral': {
        'preprocessing': Sequential([
            Absolute(),
            SumChannel(),
            Normalize(),
            Flatten()
        ]),
        'distance': SciPyPDist(metric='euclidean'),
    },
    'spectral': {
        'preprocessing': Sequential([
            SumChannel(),
            Normalize(),
            Flatten()
        ]),
        'distance': SciPyPDist(metric='euclidean'),
    },
    'fullspectral': {
        'preprocessing': Sequential([
            Normalize(axes=(1, 2, 3)),
            Flatten()
        ]),
        'distance': SciPyPDist(metric='euclidean'),
    },
    'histogram': {
        'preprocessing': Sequential([
            Normalize(axes=(1, 2, 3)),
            Histogram(),
            Flatten()
        ]),
        'distance': SciPyPDist(metric='euclidean'),
    },
}


def meta_analysis(
        attribution_file_path: str,
        analysis_file_path: str,
        variant: str,
        class_indices: List[int],
        label_map_file_path: str,
        number_of_eigenvalues: int,
        number_of_clusters_list: List[int],
        number_of_neighbors: int) -> None:
    """Performs a meta-analysis over the specified attribution data and writes the results into an analysis database.

    Parameters
    ----------
        attribution_file_path: str
            The path to the attribution database file, that contains the attributions for which the meta-analysis is to
            be performed.
        analysis_file_path: str
            The path to the analysis database file, into which the results of the meta-analysis are to be written.
        variant: str
            The meta-analysis variant that is to be performed. Can be one of "absspectral", "spectral", "fullspectral",
            or "histogram".
        class_indices: List[int]
            The indices of the classes for which the meta-analysis is to be performed. If not specified, then the
            meta-analysis is performed for all classes.
        label_map_file_path: str
            The path to the label map file, which contains a mapping between the class indices and their corresponding
            names and WordNet IDs.
        number_of_eigenvalues: int
            The number of eigenvalues of the eigenvalue decomposition.
        number_of_clusters_list: List[int]
            A list that can contain multiple numbers of clusters. For each number of clusters in this list, all
            clustering methods and the meta-analysis are performed.
        number_of_neighbors: int
            The number of neighbors that are to be considered in the k-nearest neighbor clustering algorithm.
    """

    # Determines the pre-processing pipeline and the distance metric that are to be used for the meta-analysis
    pre_processing_pipeline = VARIANTS[variant]['preprocessing']
    distance_metric = VARIANTS[variant]['distance']

    # Creates the meta-analysis pipeline
    pipeline = SpectralClustering(
        preprocessing=pre_processing_pipeline,
        pairwise_distance=distance_metric,
        affinity=SparseKNN(n_neighbors=number_of_neighbors, symmetric=True),
        embedding=EigenDecomposition(n_eigval=number_of_eigenvalues, is_output=True),
        clustering=Parallel([
            Parallel([
                KMeans(n_clusters=number_of_clusters) for number_of_clusters in number_of_clusters_list
            ], broadcast=True),
            Parallel([
                DBSCAN(eps=number_of_clusters / 10.0) for number_of_clusters in number_of_clusters_list
            ], broadcast=True),
            HDBSCAN(),
            Parallel([
                AgglomerativeClustering(n_clusters=number_of_clusters) for number_of_clusters in number_of_clusters_list
            ], broadcast=True),
            Parallel([
                UMAPEmbedding(),
                TSNEEmbedding(),
            ], broadcast=True)
        ], broadcast=True, is_output=True)
    )

    # Loads the label map and converts it to a dictionary, which maps the class index to its WordNet ID
    if label_map_file_path is not None:
        with open(label_map_file_path, 'r', encoding='utf-8') as label_map_file:
            label_map = json.load(label_map_file)
        wordnet_id_map = {label['index']: label['word_net_id'] for label in label_map}
        class_name_map = {label['index']: label['name'] for label in label_map}
    else:
        wordnet_id_map = {}
        class_name_map = {}

    # Retrieves the labels of the samples
    with h5py.File(attribution_file_path, 'r') as attributions_file:
        labels = attributions_file['label'][:]

    # Gets the indices of the classes for which the meta-analysis is to be performed, if non were specified, the the
    # meta-analysis is performed for all classes
    if class_indices is None:
        class_indices = [int(label['index']) for label in label_map]

    # Truncate the analysis database
    print(f'Truncating {analysis_file_path}')
    h5py.File(analysis_file_path, 'w').close()

    # Cycles through all classes and performs the meta-analysis for each of them
    for class_index in class_indices:

        # Loads the attribution data for the samples of the current class
        print(f'Loading class {class_name_map[class_index]}')
        with h5py.File(attribution_file_path, 'r') as attributions_file:
            indices_of_samples_in_class, = numpy.nonzero(labels == class_index)
            attribution_data = attributions_file['attribution'][indices_of_samples_in_class, :]
            if 'train' in attributions_file:
                train_flag = attributions_file['train'][indices_of_samples_in_class.tolist()]
            else:
                train_flag = None

        # Performs the meta-analysis for the attributions of the current class
        print(f'Computing class {class_name_map[class_index]}')
        (eigenvalues, embedding), (kmeans, dbscan, hdbscan, agglomerative, (umap, tsne)) = pipeline(attribution_data)

        # Append the meta-analysis to the analysis database
        print(f'Saving class {class_name_map[class_index]}')
        with h5py.File(analysis_file_path, 'a') as analysis_file:

            # The name of the analysis is the name of the class
            analysis_name = wordnet_id_map.get(class_index, f'{class_index:08d}')

            # Adds the indices of the samples in the current class to the analysis database
            analysis_group = analysis_file.require_group(analysis_name)
            analysis_group['index'] = indices_of_samples_in_class.astype('uint32')

            # Adds the spectral embedding to the analysis database
            embedding_group = analysis_group.require_group('embedding')
            embedding_group['spectral'] = embedding.astype(numpy.float32)
            embedding_group['spectral'].attrs['eigenvalue'] = eigenvalues.astype(numpy.float32)

            # Adds the t-SNE embedding to the analysis database
            embedding_group['tsne'] = tsne.astype(numpy.float32)
            embedding_group['tsne'].attrs['embedding'] = 'spectral'
            embedding_group['tsne'].attrs['index'] = numpy.array([0, 1])

            # Adds the uMap embedding to the analysis database
            embedding_group['umap'] = umap.astype(numpy.float32)
            embedding_group['umap'].attrs['embedding'] = 'spectral'
            embedding_group['umap'].attrs['index'] = numpy.array([0, 1])

            # Adds the k-means clustering of the embeddings to the analysis database
            cluster_group = analysis_group.require_group('cluster')
            for number_of_clusters, clustering in zip(number_of_clusters_list, kmeans):
                clustering_dataset_name = f'kmeans-{number_of_clusters:02d}'
                cluster_group[clustering_dataset_name] = clustering
                cluster_group[clustering_dataset_name].attrs['embedding'] = 'spectral'
                cluster_group[clustering_dataset_name].attrs['k'] = number_of_clusters
                cluster_group[clustering_dataset_name].attrs['index'] = numpy.arange(
                    embedding.shape[1],
                    dtype=numpy.uint32
                )

            # Adds the DBSCAN epsilon clustering of the embeddings to the analysis database
            for number_of_clusters, clustering in zip(number_of_clusters_list, dbscan):
                clustering_dataset_name = f'dbscan-eps={number_of_clusters / 10.0:.1f}'
                cluster_group[clustering_dataset_name] = clustering
                cluster_group[clustering_dataset_name].attrs['embedding'] = 'spectral'
                cluster_group[clustering_dataset_name].attrs['index'] = numpy.arange(
                    embedding.shape[1],
                    dtype=numpy.uint32
                )

            # Adds the HDBSCAN clustering of the embeddings to the analysis database
            clustering_dataset_name = 'hdbscan'
            cluster_group[clustering_dataset_name] = hdbscan
            cluster_group[clustering_dataset_name].attrs['embedding'] = 'spectral'
            cluster_group[clustering_dataset_name].attrs['index'] = numpy.arange(
                embedding.shape[1],
                dtype=numpy.uint32
            )

            # Adds the Agglomerative clustering of the embeddings to the analysis database
            for number_of_clusters, clustering in zip(number_of_clusters_list, agglomerative):
                clustering_dataset_name = f'agglomerative-{number_of_clusters:02d}'
                cluster_group[clustering_dataset_name] = clustering
                cluster_group[clustering_dataset_name].attrs['embedding'] = 'spectral'
                cluster_group[clustering_dataset_name].attrs['k'] = number_of_clusters
                cluster_group[clustering_dataset_name].attrs['index'] = numpy.arange(
                    embedding.shape[1],
                    dtype=numpy.uint32
                )

            # If the attributions were computed on the training split of the dataset, then the training flag is set
            if train_flag is not None:
                cluster_group['train_split'] = train_flag


def main() -> None:
    """The entrypoint to the meta_analysis script."""

    argument_parser = argparse.ArgumentParser(
        prog='meta_analysis',
        description='''Performs a meta-analysis on an attribution database and writes them into an analysis database,
            from which a ViRelAy project can be created.
        '''
    )
    argument_parser.add_argument(
        'attribution_file_path',
        type=str,
        help='''The path to the attribution database file, that contains the attributions for which the meta-analysis is
            to be performed.
        '''
    )
    argument_parser.add_argument(
        'analysis_file_path',
        type=str,
        help='The path to the analysis database file, into which the results of the meta-analysis are to be written.'
    )
    argument_parser.add_argument(
        '-V',
        '--variant',
        dest='variant',
        type=str,
        choices=['absspectral', 'spectral', 'fullspectral', 'histogram'],
        default='spectral',
        help='The meta-analysis variant that is to be performed. Defaults to "spectral".'
    )
    argument_parser.add_argument(
        '-c',
        '--class-indices',
        dest='class_indices',
        type=int,
        nargs='*',
        help='''The indices of the classes for which the meta-analysis is to be performed. If not specified, then the
            meta-analysis is performed for all classes.
        '''
    )
    argument_parser.add_argument(
        '-l',
        '--label-map-file-path',
        dest='label_map_file_path',
        type=str,
        help='''The path to the label map file, which contains a mapping between the class indices and their
            corresponding names and WordNet IDs.
        '''
    )
    argument_parser.add_argument(
        '-e',
        '--number-of-eigenvalues',
        dest='number_of_eigenvalues',
        type=int,
        default=32,
        help='The number of eigenvalues of the eigenvalue decomposition. Defaults to 32.'
    )
    argument_parser.add_argument(
        '-n',
        '--number-of-neighbors',
        dest='number_of_neighbors',
        type=int,
        default=32,
        help='''The number of neighbors that are to be considered in the k-nearest neighbor clustering algorithm.
            Defaults to 32.
        '''
    )
    argument_parser.add_argument(
        '-C',
        '--number-of-clusters-list',
        dest='number_of_clusters_list',
        type=int,
        nargs='*',
        default=list(range(2, 31)),
        help='''A list that can contain multiple numbers of clusters. For each number of clusters in this list, all
            clustering methods and the meta-analysis are performed. Defaults to a list from 2 to 30 clusters.
        '''
    )
    arguments = argument_parser.parse_args()

    meta_analysis(
        arguments.attribution_file_path,
        arguments.analysis_file_path,
        arguments.variant,
        arguments.class_indices,
        arguments.label_map_file_path,
        arguments.number_of_eigenvalues,
        arguments.number_of_clusters_list,
        arguments.number_of_neighbors
    )


if __name__ == '__main__':
    main()
