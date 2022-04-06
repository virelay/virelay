"""Contains the tests for the model abstractions of ViRelAy"""

import os
import json
import pathlib

import yaml
import h5py
import numpy
import pytest

from virelay.model import LabelMap
from corelay.processor.base import Processor
from corelay.processor.flow import Sequential, Parallel
from corelay.processor.distance import SciPyPDist
from corelay.pipeline.spectral import SpectralClustering
from corelay.processor.clustering import KMeans, DBSCAN, HDBSCAN, AgglomerativeClustering
from corelay.processor.embedding import TSNEEmbedding, UMAPEmbedding, EigenDecomposition
from corelay.processor.affinity import SparseKNN

NUMBER_OF_CLASSES = 3
NUMBER_OF_SAMPLES = 10


class Flatten(Processor):
    """Represents a processor, which flattens the data."""

    def function(self, data: numpy.ndarray) -> numpy.ndarray:
        """Applies the processor to the data.

        Parameters
        ----------
            data (numpy.ndarray): The data that is to be processed.

        Returns
        -------
            numpy.ndarray:
                Returns the processed data.
        """

        return data.reshape(data.shape[0], numpy.prod(data.shape[1:]))


class SumChannel(Processor):
    """Represents a processor, which produces the sum over the channels of the data."""

    def function(self, data: numpy.ndarray) -> numpy.ndarray:
        """Applies the processor to the data.

        Parameters
        ----------
            data (numpy.ndarray): The data that is to be processed.

        Returns
        -------
            numpy.ndarray:
                Returns the processed data.
        """

        return data.sum(1)


class Normalize(Processor):
    """Represents a processor, which normalizes the data."""

    def function(self, data: numpy.ndarray) -> numpy.ndarray:
        """Applies the processor to the data.

        Parameters
        ----------
            data (numpy.ndarray): The data that is to be processed.

        Returns
        -------
            numpy.ndarray:
                Returns the processed data.
        """

        data = data / data.sum((1, 2), keepdims=True)
        return data


@pytest.fixture(scope='function')
def label_map_file_path(tmp_path: pathlib.Path) -> str:
    """A test fixture, which creates a label map file.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory in which the label file will be created. This a an automatically created
            temporary path and comes from the built-in tmp_path fixture of PyTest.

    Returns
    -------
        str
            Returns the path to the created label map file.
    """

    label_map = [
        {
            'index': i,
            'word_net_id': f'{i:08d}',
            'name': f'Class {i:d}',
        } for i in range(NUMBER_OF_CLASSES)
    ]

    label_map_file_path = tmp_path / 'label-map.json'
    with open(label_map_file_path, 'w', encoding='utf-8') as label_map_file:
        json.dump(label_map, label_map_file)

    return label_map_file_path.as_posix()


@pytest.fixture(scope='function')
def input_file_path(tmp_path: pathlib.Path) -> str:
    """A test fixture, which creates an input file.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory in which the input file will be created. This a an automatically created
            temporary path and comes from the built-in tmp_path fixture of PyTest.

    Returns
    -------
        str
            Returns the path to the created input file.
    """

    input_file_path = tmp_path / 'input.h5'
    for label in range(NUMBER_OF_CLASSES):

        data = numpy.random.uniform(0, 1, size=(NUMBER_OF_SAMPLES, 3, 32, 32))
        data_labels = numpy.array([label] * NUMBER_OF_SAMPLES)

        with h5py.File(input_file_path, 'w') as input_file:
            input_file.create_dataset('data', shape=(NUMBER_OF_SAMPLES, 3, 32, 32), dtype='float32', data=data)
            input_file.create_dataset('label', shape=(NUMBER_OF_SAMPLES,), dtype='uint16', data=data_labels)

    return input_file_path.as_posix()


@pytest.fixture(scope='function')
def attribution_file_path(tmp_path: pathlib.Path) -> str:
    """A test fixture, which creates an attribution file.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory in which the attribution file will be created. This a an automatically
            created temporary path and comes from the built-in tmp_path fixture of PyTest.

    Returns
    -------
        str
            Returns the path to the created attribution file.
    """

    attribution_file_path = tmp_path / 'attribution.h5'
    for label in range(NUMBER_OF_CLASSES):

        attributions = numpy.random.uniform(-1, 1, size=(NUMBER_OF_SAMPLES, 3, 32, 32))
        predictions = numpy.random.uniform(0, 1, size=(NUMBER_OF_SAMPLES, NUMBER_OF_CLASSES))
        data_labels = numpy.array([label] * NUMBER_OF_SAMPLES)

        with h5py.File(attribution_file_path, 'w') as input_file:
            input_file.create_dataset(
                'attribution',
                shape=(NUMBER_OF_SAMPLES, 3, 32, 32),
                dtype='float32',
                data=attributions
            )
            input_file.create_dataset(
                'prediction',
                shape=(NUMBER_OF_SAMPLES, NUMBER_OF_CLASSES),
                dtype='float32',
                data=predictions
            )
            input_file.create_dataset('label', shape=(NUMBER_OF_SAMPLES,), dtype='uint16', data=data_labels)

    return attribution_file_path.as_posix()


@pytest.fixture(scope='function')
def analysis_file_path(tmp_path: pathlib.Path, attribution_file_path: str, label_map_file_path: str) -> str:
    """A test fixture, which creates an analysis file.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory in which the analysis file will be created. This a an automatically
            created temporary path and comes from the built-in tmp_path fixture of PyTest.
        attribution_file_path: str
            The path to the attribution file that contains the attributions for which the analysis is to be generated.
            This comes from the attribution_file_path fixture.
        label_map_file_path: str
            The path to the label map file. This comes from the label_map_file_path fixture.

    Returns
    -------
        str
            Returns the path to the created analysis file.
    """

    analysis_file_path = tmp_path / 'analysis.h5'

    number_of_clusters_to_try = [2, 3]
    analysis_pipeline = SpectralClustering(
        preprocessing=Sequential([
            SumChannel(),
            Normalize(),
            Flatten()
        ]),
        pairwise_distance=SciPyPDist(metric='euclidean'),
        affinity=SparseKNN(n_neighbors=32, symmetric=True),
        embedding=EigenDecomposition(n_eigval=32, is_output=True),
        clustering=Parallel([
            Parallel([
                KMeans(n_clusters=number_of_clusters) for number_of_clusters in number_of_clusters_to_try
            ], broadcast=True),
            Parallel([
                DBSCAN(eps=number_of_clusters / 10.0) for number_of_clusters in number_of_clusters_to_try
            ], broadcast=True),
            HDBSCAN(),
            Parallel([
                AgglomerativeClustering(n_clusters=k) for k in number_of_clusters_to_try
            ], broadcast=True),
            Parallel([
                UMAPEmbedding(),
                TSNEEmbedding(),
            ], broadcast=True)
        ], broadcast=True, is_output=True)
    )

    with open(label_map_file_path, 'r', encoding='utf-8') as label_map_file:
        label_map = json.load(label_map_file)
    label_map = {element['index']: element['word_net_id'] for element in label_map}

    with h5py.File(attribution_file_path, 'r') as attribution_file, h5py.File(analysis_file_path, 'w') as analysis_file:

        data_labels = attribution_file['label'][:]

        for class_index in [int(element) for element in label_map]:
            index, = numpy.nonzero(data_labels == class_index)
            data = attribution_file['attribution'][index, :]

            (eigenvalues, embedding), (kmeans, dbscan, hdbscan, agglo, (umap, tsne)) = analysis_pipeline(data)

            analysis_name = label_map.get(class_index, f'{class_index:03d}')
            analysis_group = analysis_file.require_group(analysis_name)
            analysis_group['index'] = index.astype('uint32')

            embedding_group = analysis_group.require_group('embedding')
            embedding_group['spectral'] = embedding.astype('float32')
            embedding_group['spectral'].attrs['eigenvalue'] = eigenvalues.astype('float32')

            embedding_group['tsne'] = tsne.astype('float32')
            embedding_group['tsne'].attrs['embedding'] = 'spectral'
            embedding_group['tsne'].attrs['index'] = numpy.array([0, 1])

            embedding_group['umap'] = umap.astype('float32')
            embedding_group['umap'].attrs['embedding'] = 'spectral'
            embedding_group['umap'].attrs['index'] = numpy.array([0, 1])

            cluster_group = analysis_group.require_group('cluster')
            for number_of_clusters, clustering in zip(number_of_clusters_to_try, kmeans):
                cluster_id = f'kmeans-{number_of_clusters:02d}'
                cluster_group[cluster_id] = clustering
                cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                cluster_group[cluster_id].attrs['k'] = number_of_clusters
                cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype='uint32')

            for number_of_clusters, clustering in zip(number_of_clusters_to_try, dbscan):
                cluster_id = f'dbscan-eps={number_of_clusters / 10.0:.1f}'
                cluster_group[cluster_id] = clustering
                cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype='uint32')

            cluster_id = 'hdbscan'
            cluster_group[cluster_id] = hdbscan
            cluster_group[cluster_id].attrs['embedding'] = 'spectral'
            cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype='uint32')

            for number_of_clusters, clustering in zip(number_of_clusters_to_try, agglo):
                cluster_id = f'agglomerative-{number_of_clusters:02d}'
                cluster_group[cluster_id] = clustering
                cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                cluster_group[cluster_id].attrs['k'] = number_of_clusters
                cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype='uint32')

    return analysis_file_path.as_posix()


@pytest.fixture(scope='function')
def project_file_path(
        tmp_path: pathlib.Path,
        input_file_path: str,
        attribution_file_path: str,
        analysis_file_path: str,
        label_map_file_path: str) -> str:
    """A test fixture, which creates an project file.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory in which the project file will be created. This a an automatically created
            temporary path and comes from the built-in tmp_path fixture of PyTest.
        input_file_path: str
            The path to the input file. This comes from the input_file_path fixture.
        attribution_file_path: str
            The path to the attribution file. This comes from the attribution_file_path fixture.
        analysis_file_path: str
            The path to the analysis file. This comes from the analysis_file_path fixture.
        label_map_file_path: str
            The path to the label map file. This comes from the label_map_file_path fixture.

    Returns
    -------
        str
            Returns the path to the created project file.
    """

    project_file_path = tmp_path / 'project.yaml'

    project = {
        'project': {
            'name': 'Test Project',
            'model': 'No Model',
            'label_map': os.path.relpath(label_map_file_path, start=tmp_path.as_posix()),
            'dataset': {
                'name': "Random Data",
                'type': 'hdf5',
                'path': os.path.relpath(input_file_path, start=tmp_path.as_posix()),
                'input_width': 32,
                'input_height': 32,
                'down_sampling_method': 'none',
                'up_sampling_method': 'none',
            },
            'attributions': {
                'attribution_method': 'Random Attribution',
                'attribution_strategy': 'true_label',
                'sources': [os.path.relpath(attribution_file_path, start=tmp_path.as_posix())],
            },
            'analyses': [
                {
                    'analysis_method': 'Spectral Analysis',
                    'sources': [os.path.relpath(analysis_file_path, start=tmp_path.as_posix())]
                }
            ]
        }
    }

    with open(project_file_path, 'w', encoding='utf-8') as project_file:
        yaml.dump(project, project_file, default_flow_style=False)

    return project_file_path.as_posix()


class TestLabelMap:
    """Represents the tests for the LabelMap class."""

    @staticmethod
    def test_label_map(label_map_file_path: str) -> None:
        """Tests the label map.

        Parameters
        ----------
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        # Loads the label map file
        label_map = LabelMap(label_map_file_path)

        # Checks if labels can be retrieved via index
        assert label_map.get_label_from_index(0) == 'Class 0'
        with pytest.raises(LookupError):
            label_map.get_label_from_index(3)

        # Checks if labels can be retrieved via WordNet IDs
        assert label_map.get_label_from_word_net_id('00000001') == 'Class 1'
        with pytest.raises(LookupError):
            label_map.get_label_from_word_net_id("")
        with pytest.raises(LookupError):
            label_map.get_labels_from_n_hot_vector(numpy.array([0, 0, 0, 1]))

        # Checks if labels can be retrieved via one-hot encoded vectors
        assert label_map.get_labels_from_n_hot_vector(numpy.array([1, 0, 1])) == ['Class 0', 'Class 2']

        # Checks whether the generic label retrieval method supports all formats
        assert label_map.get_labels(numpy.array([0])[0]) == 'Class 0'
        assert label_map.get_labels(1) == 'Class 1'
        assert label_map.get_labels('00000002') == 'Class 2'
        assert label_map.get_labels(numpy.array([1, 1, 0])) == ['Class 0', 'Class 1']
        with pytest.raises(LookupError):
            label_map.get_labels([])
