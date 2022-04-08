"""Contains the tests for the model abstractions of ViRelAy."""
# pylint: disable=too-many-lines

import os
import glob
import json
import random
import pathlib

import yaml
import h5py
import numpy
import pytest
from PIL import Image

from corelay.processor.base import Processor
from corelay.processor.affinity import SparseKNN
from corelay.processor.distance import SciPyPDist
from corelay.processor.flow import Sequential, Parallel
from corelay.pipeline.spectral import SpectralClustering
from corelay.processor.clustering import KMeans, DBSCAN, HDBSCAN, AgglomerativeClustering
from corelay.processor.embedding import TSNEEmbedding, UMAPEmbedding, EigenDecomposition
from virelay.model import (
    Project,
    AttributionDatabase,
    Attribution,
    AnalysisDatabase,
    Analysis,
    AnalysisCategory,
    Hdf5Dataset,
    ImageDirectoryDataset,
    Sample,
    LabelMap,
    Label,
    Workspace
)

NUMBER_OF_CLASSES = 3
NUMBER_OF_SAMPLES = 40


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
            'index': label_index,
            'word_net_id': f'{label_index:08d}',
            'name': f'Class {label_index:d}',
        } for label_index in range(NUMBER_OF_CLASSES)
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

    data = None
    data_labels = None
    input_file_path = tmp_path / 'input.h5'
    for label_index in range(NUMBER_OF_CLASSES):

        new_data = numpy.random.uniform(0, 1, size=(NUMBER_OF_SAMPLES, 3, 32, 32))
        if data is None:
            data = new_data
        else:
            data = numpy.concatenate((data, new_data), axis=0)
        new_data_labels = numpy.array([label_index] * NUMBER_OF_SAMPLES)
        if data_labels is None:
            data_labels = new_data_labels
        else:
            data_labels = numpy.concatenate((data_labels, new_data_labels), axis=0)

    with h5py.File(input_file_path, 'w') as input_file:
        input_file.create_dataset(
            'data',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, 3, 32, 32),
            dtype='float32',
            data=data
        )
        input_file.create_dataset(
            'label',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES,),
            dtype='uint16',
            data=data_labels
        )

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

    attributions = None
    predictions = None
    data_labels = None
    attribution_file_path = tmp_path / 'attribution.h5'
    for label_index in range(NUMBER_OF_CLASSES):

        new_attributions = numpy.random.uniform(-1, 1, size=(NUMBER_OF_SAMPLES, 3, 32, 32))
        if attributions is None:
            attributions = new_attributions
        else:
            attributions = numpy.concatenate((attributions, new_attributions), axis=0)
        new_predictions = numpy.random.uniform(0, 1, size=(NUMBER_OF_SAMPLES, NUMBER_OF_CLASSES))
        if predictions is None:
            predictions = new_predictions
        else:
            predictions = numpy.concatenate((predictions, new_predictions), axis=0)
        new_data_labels = numpy.array([label_index] * NUMBER_OF_SAMPLES)
        if data_labels is None:
            data_labels = new_data_labels
        else:
            data_labels = numpy.concatenate((data_labels, new_data_labels), axis=0)

    with h5py.File(attribution_file_path, 'w') as input_file:
        input_file.create_dataset(
            'attribution',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, 3, 32, 32),
            dtype='float32',
            data=attributions
        )
        input_file.create_dataset(
            'prediction',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, NUMBER_OF_CLASSES),
            dtype='float32',
            data=predictions
        )
        input_file.create_dataset(
            'label',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES,),
            dtype='uint16',
            data=data_labels
        )

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

        for label_index in [int(element) for element in label_map]:
            index, = numpy.nonzero(data_labels == label_index)
            data = attribution_file['attribution'][index, :]

            (eigenvalues, embedding), (kmeans, dbscan, hdbscan, agglo, (umap, tsne)) = analysis_pipeline(data)

            analysis_name = label_map.get(label_index, f'{label_index:03d}')
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


@pytest.fixture(scope='function')
def image_directory_dataset_with_label_indices_path(tmp_path: pathlib.Path) -> str:
    """A test fixture, which creates an image dataset, where the image files are in a directory hierarchy were the names
    of the directories represent the labels of the images. In this version of the fixture, the label directories have
    the index of the label in them.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory in which the project file will be created. This a an automatically created
            temporary path and comes from the built-in tmp_path fixture of PyTest.

    Returns
    -------
        str
            Returns the path to the created image dataset.
    """

    image_directory_dataset_path = tmp_path / 'image-dataset-with-label-indices'
    image_directory_dataset_path.mkdir()

    for label_index in range(NUMBER_OF_CLASSES):
        label_directory_path = image_directory_dataset_path / f'label-{label_index}'
        label_directory_path.mkdir()

        for image_index in range(NUMBER_OF_SAMPLES):
            image = Image.new(
                'RGB',
                (64, 64),
                color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
            image.save(label_directory_path / f'image-{image_index}.png')

    return image_directory_dataset_path.as_posix()


@pytest.fixture(scope='function')
def image_directory_dataset_with_wordnet_ids_path(tmp_path: pathlib.Path) -> str:
    """A test fixture, which creates an image dataset, where the image files are in a directory hierarchy were the names
    of the directories represent the labels of the images. In this version of the fixture, the label directories have
    the WordNet ID of the label in them.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory in which the project file will be created. This a an automatically created
            temporary path and comes from the built-in tmp_path fixture of PyTest.

    Returns
    -------
        str
            Returns the path to the created image dataset.
    """

    image_directory_dataset_path = tmp_path / 'image-dataset-with-label-indices'
    image_directory_dataset_path.mkdir()

    for label_index in range(NUMBER_OF_CLASSES):
        label_directory_path = image_directory_dataset_path / f'wordnet-{label_index:08d}'
        label_directory_path.mkdir()

        for image_index in range(NUMBER_OF_SAMPLES):
            image = Image.new(
                'RGB',
                (64, 64),
                color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
            image.save(label_directory_path / f'image-{image_index}.png')

    return image_directory_dataset_path.as_posix()


@pytest.fixture(scope='function')
def image_directory_dataset_with_sample_paths_file_path(tmp_path: pathlib.Path) -> str:
    """A test fixture, which creates an image dataset, where the image files are in a directory hierarchy were the names
    of the directories represent the labels of the images. In this version of the fixture, a file exists, which lists
    all samples of the dataset. Only every second image is actually added to the sample paths file, so that it can be
    validated that the dataset actually loaded the samples from the sample paths file.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory in which the project file will be created. This a an automatically created
            temporary path and comes from the built-in tmp_path fixture of PyTest.

    Returns
    -------
        str
            Returns the path to the created image dataset.
    """

    image_directory_dataset_path = tmp_path / 'image-dataset-with-sample-paths-file'
    image_directory_dataset_path.mkdir()

    image_file_paths = []
    for label_index in range(NUMBER_OF_CLASSES):
        label_directory_path = image_directory_dataset_path / f'label-{label_index}'
        label_directory_path.mkdir()

        for image_index in range(NUMBER_OF_SAMPLES):
            image = Image.new(
                'RGB',
                (64, 64),
                color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
            image_file_path = label_directory_path / f'image-{image_index}.png'
            image.save(image_file_path)
            image_file_paths.append(image_file_path.as_posix())

    with open(image_directory_dataset_path.as_posix() + '_paths.txt', 'w', encoding='utf-8') as sample_paths_file:
        sample_paths_file.write('\n'.join(image_file_paths[::2]))

    return image_directory_dataset_path.as_posix()


class TestProject:
    """Represents the tests for the Project class."""

    @staticmethod
    def test_project_creation(project_file_path: str) -> None:
        """Tests whether a project can be created.

        Parameters
        ----------
            project_file_path: str
                The path to the project file that is used for the tests.
        """

        project = Project(project_file_path)
        assert not project.is_closed
        assert project.name == 'Test Project'
        assert project.model == 'No Model'
        assert project.dataset.name == 'Random Data'
        assert project.attribution_method == 'Random Attribution'
        assert len(project.analyses) == 1
        assert 'Spectral Analysis' in project.analyses


class TestAttributionDatabase:
    """Represents the tests for the AttributionDatabase class."""

    @staticmethod
    def test_attribution_database_creation(attribution_file_path: str, label_map_file_path: str) -> None:
        """Tests whether an attribution database can be created.


        Parameters
        ----------
            attribution_file_path: str
                The path to the attributions file that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        attribution_database = AttributionDatabase(attribution_file_path, label_map_file_path)
        assert not attribution_database.is_closed
        assert not attribution_database.is_multi_label


class TestAttribution:
    """Represents the tests for the Attribution class."""

    @staticmethod
    def test_attribution_creation() -> None:
        """Tests whether an attribution can be created."""

        data = numpy.random.uniform(-1, 1, size=(32, 32, 3))
        label_0 = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label_0, prediction)

        assert attribution.index == 0
        assert numpy.array_equal(attribution.data, data)
        assert attribution.labels == [label_0]
        assert numpy.array_equal(attribution.prediction, prediction)

        data = numpy.random.uniform(-1, 1, size=(32, 32, 3))
        label_1 = Label(1, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(1, data, [label_0, label_1], prediction)

        assert attribution.index == 1
        assert numpy.array_equal(attribution.data, data)
        assert attribution.labels == [label_0, label_1]
        assert numpy.array_equal(attribution.prediction, prediction)

        data = numpy.random.uniform(-1, 1, size=(3, 32, 32))
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(2, data, label_0, prediction)

        assert attribution.index == 2
        assert numpy.array_equal(attribution.data, numpy.moveaxis(data, [0, 1, 2], [2, 0, 1]))
        assert attribution.labels == [label_0]
        assert numpy.array_equal(attribution.prediction, prediction)

    @staticmethod
    def test_attribution_render_heatmap_unknown_color_map():
        """Tests whether the heatmap rendering of the attribution fails, when the color map is unknown."""

        data = numpy.random.uniform(-1, 1, size=(4, 4, 3))
        label = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label, prediction)
        with pytest.raises(ValueError):
            attribution.render_heatmap('unknown-color-map')

    @staticmethod
    def test_attribution_render_heatmap():
        """Tests whether a heatmap can be rendered from the attribution."""

        # Creates the attribution
        data = numpy.array(
            [[[-0.63598313, 0.05182445, -0.94523354],
              [0.21506858, -0.13204615, 0.0819828],
              [0.10219199, -0.49505036, -0.57652793],
              [0.01718352, 0.0409061, 0.58327392]],
             [[0.86893207, -0.26937166, -0.94142186],
              [-0.61266463, -0.09961933, -0.80746353],
              [-0.91493128, -0.31382453, 0.04481068],
              [-0.39876502, -0.28151701, 0.93280041]],
             [[0.28490411, 0.47067797, 0.40586151],
              [-0.3422943, 0.91319999, -0.98634023],
              [0.81298836, 0.39517061, 0.76021407],
              [0.10702649, -0.62526615, -0.34403102]],
             [[-0.27316466, 0.93960925, 0.03727774],
              [0.83324282, -0.69104866, 0.50410142],
              [0.86643333, 0.50700986, 0.16282292],
              [-0.71744439, 0.27219448, 0.34797268]]]
        )
        label = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label, prediction)

        # Validates the colors assigned by the heatmap
        expected_heatmap = numpy.array(
            [[[56, 56, 255],
              [255, 234, 234],
              [128, 128, 255],
              [255, 172, 172]],
             [[210, 210, 255],
              [58, 58, 255],
              [102, 102, 255],
              [255, 222, 222]],
             [[255, 104, 104],
              [200, 200, 255],
              [255, 0, 0],
              [142, 142, 255]],
             [[255, 163, 163],
              [255, 170, 170],
              [255, 56, 56],
              [242, 242, 255]]],
            dtype=numpy.uint8
        )
        actual_heatmap = attribution.render_heatmap('blue-white-red')
        assert numpy.array_equal(expected_heatmap, actual_heatmap)

    @staticmethod
    def test_attribution_render_superimposed_heatmap_unknown_color_map():
        """Tests the rendering of heatmap images that are then superimposed onto another image using the attribution
        data as alpha-channel using an unknown color map."""

        data = numpy.random.uniform(-1, 1, size=(4, 4, 3))
        label = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label, prediction)
        superimpose = numpy.ones((4, 4, 3))
        with pytest.raises(ValueError):
            attribution.render_heatmap('unknown-color-map', superimpose)

    @staticmethod
    def test_attribution_render_superimposed_heatmap():
        """Tests whether a heatmap, superimposed onto another image, can be rendered from the attribution."""

        # Creates the attribution
        data = numpy.array(
            [[[0.17681855, 0.91944598, 0.33373127],
              [-0.80632149, -0.93380861, 0.15624767],
              [-0.80029563, -0.10224675, -0.21737921],
              [-0.12587663, 0.00244791, 0.0558195]],
             [[0.34478494, 0.22592281, -0.46938452],
              [-0.28683651, -0.43241806, -0.74974368],
              [0.28910623, 0.9201011, 0.69483512],
              [0.60624353, 0.58788177, 0.05531979]],
             [[-0.52632942, 0.95181703, -0.12907603],
              [0.11709027, -0.78199527, -0.3564949],
              [-0.02690579, 0.30163809, 0.15051245],
              [0.29140564, 0.79343594, -0.43470242]],
             [[-0.43761021, 0.27552307, 0.028462],
              [-0.37463762, -0.09987923, 0.65990991],
              [0.46209578, 0.72126955, 0.50027807],
              [0.68741856, 0.13709213, 0.92287532]]]
        )
        label = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label, prediction)
        superimpose = numpy.ones((4, 4, 3))

        # Validates the colors assigned by the heatmap
        expected_heatmap = numpy.array(
            [[[172, 42, 42],
              [38, 38, 229],
              [66, 66, 162],
              [10, 10, 10]],
             [[13, 12, 12],
              [48, 48, 212],
              [229, 0, 0],
              [150, 52, 52]],
             [[36, 31, 31],
              [68, 68, 147],
              [52, 40, 40],
              [79, 52, 52]],
             [[19, 19, 20],
              [23, 21, 21],
              [202, 22, 22],
              [210, 17, 17]]],
            dtype=numpy.uint8
        )
        actual_heatmap = attribution.render_heatmap('blue-white-red', superimpose)
        assert numpy.array_equal(expected_heatmap, actual_heatmap)


class TestAnalysisDatabase:
    """Represents the tests for the AnalysisDatabase class."""

    @staticmethod
    def test_analysis_database_creation(analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether an analysis database can be created.


        Parameters
        ----------
            analysis_file_path: str
                The path to the attributions file that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        analysis_database = AnalysisDatabase(analysis_file_path, label_map_file_path)
        assert not analysis_database.is_closed


class TestAnalysisCategory:
    """Represents the tests for the AnalysisCategory class."""

    @staticmethod
    def test_analysis_category_creation() -> None:
        """Tests whether an analysis category can be created."""

        analysis_category = AnalysisCategory('class-0', 'Class 0')
        assert analysis_category.name == 'class-0'
        assert analysis_category.human_readable_name == 'Class 0'


class TestAnalysis:
    """Represents the tests for the Analysis class."""

    @staticmethod
    def test_analysis_creation() -> None:
        """Tests whether an analysis can be created."""

        clustering = numpy.random.randint(NUMBER_OF_CLASSES, size=NUMBER_OF_SAMPLES)
        embedding = numpy.random.uniform(size=(NUMBER_OF_CLASSES, 16))
        attribution_indices = numpy.random.randint(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES, size=NUMBER_OF_SAMPLES)
        eigen_values = numpy.random.normal(size=NUMBER_OF_SAMPLES)
        analysis = Analysis(
            category_name='class-0',
            human_readable_category_name='Class 0',
            clustering_name='kmeans-2',
            clustering=clustering,
            embedding_name='spectral',
            embedding=embedding,
            attribution_indices=attribution_indices,
            eigen_values=eigen_values,
            base_embedding_name=None,
            base_embedding_axes_indices=None
        )

        assert analysis.category_name == 'class-0'
        assert analysis.human_readable_category_name == 'Class 0'
        assert analysis.clustering_name == 'kmeans-2'
        assert numpy.array_equal(analysis.clustering, clustering)
        assert analysis.embedding_name == 'spectral'
        assert numpy.array_equal(analysis.embedding, embedding)
        assert numpy.array_equal(analysis.attribution_indices, attribution_indices)
        assert numpy.array_equal(analysis.eigen_values, eigen_values)
        assert analysis.base_embedding_name is None
        assert analysis.base_embedding_axes_indices is None


class TestHdf5Dataset:
    """Represents the tests for the Hdf5Dataset class."""

    @staticmethod
    def test_dataset_has_correct_size(
            input_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly reports its size/length.

        Parameters
        ----------
            input_file_path: str
                The path to the HDF5 dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=input_file_path,
            label_map=label_map
        )
        assert len(hdf5_dataset) == NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES

    @staticmethod
    def test_closed_dataset_cannot_retrieve_sample(
            input_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly refuses to return a sample for a closed dataset.

        Parameters
        ----------
            input_file_path: str
                The path to the HDF5 dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=input_file_path,
            label_map=label_map
        )
        hdf5_dataset.close()

        with pytest.raises(ValueError):
            hdf5_dataset.get_sample(0)

        with pytest.raises(ValueError):
            _ = hdf5_dataset[0]

    @staticmethod
    def test_dataset_can_be_closed_multiple_times(
            input_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset can be closed multiple times without raising an error.

        Parameters
        ----------
            input_file_path: str
                The path to the HDF5 dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=input_file_path,
            label_map=label_map
        )
        hdf5_dataset.close()
        hdf5_dataset.close()

    @staticmethod
    def test_cannot_retrieve_sample_for_out_of_bounds_index(
            input_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly raises an exception, when a sample is to be retrieved that is not in the
        dataset.

        Parameters
        ----------
            input_file_path: str
                The path to the HDF5 dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=input_file_path,
            label_map=label_map
        )

        with pytest.raises(LookupError):
            hdf5_dataset.get_sample(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        with pytest.raises(LookupError):
            _ = hdf5_dataset[NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES]

    @staticmethod
    def test_retrieval_of_multiple_samples(
            input_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether multiple samples can be retrieved at the same time.

        Parameters
        ----------
            input_file_path: str
                The path to the HDF5 dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=input_file_path,
            label_map=label_map
        )

        samples = hdf5_dataset[2:6]
        assert len(samples) == 4

        samples = hdf5_dataset[[2, 10, 12, 20, 19]]
        assert len(samples) == 5

        samples = hdf5_dataset[(8, 13, 27)]
        assert len(samples) == 3

        samples = hdf5_dataset[numpy.array([21, 4])]
        assert len(samples) == 2

        samples = hdf5_dataset[range(10)]
        assert len(samples) == 10


class TestImageDirectoryDataset:
    """Represents the tests for the ImageDirectoryDataset class."""

    @staticmethod
    def test_dataset_has_correct_size(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly reports its size/length.

        Parameters
        ----------
            image_directory_dataset_with_label_indices_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        assert len(image_directory_dataset) == NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES

    @staticmethod
    def test_unsupported_sampling_methods() -> None:
        """Tests whether the constructor of the image directory dataset properly raises an exception if an unsupported
        sampling method is specified.
        """

        with pytest.raises(ValueError):
            ImageDirectoryDataset(
                name="Test Dataset",
                path=None,
                label_index_regex=r'^.*/label-([0-9]+)/.*$',
                label_word_net_id_regex=None,
                input_width=64,
                input_height=64,
                down_sampling_method='unsupported',
                up_sampling_method='none',
                label_map=None
            )

        with pytest.raises(ValueError):
            ImageDirectoryDataset(
                name="Test Dataset",
                path=None,
                label_index_regex=None,
                label_word_net_id_regex=r'^.*/wordnet-([0-9]+)/.*$',
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='unsupported',
                label_map=None
            )

    @staticmethod
    def test_only_one_label_regex_must_be_specified() -> None:
        """Tests whether the constructor correctly checks if only one of the possible label RegEx's was specified."""

        with pytest.raises(ValueError):
            ImageDirectoryDataset(
                name="Test Dataset",
                path=None,
                label_index_regex=None,
                label_word_net_id_regex=None,
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='none',
                label_map=None
            )

        with pytest.raises(ValueError):
            ImageDirectoryDataset(
                name="Test Dataset",
                path=None,
                label_index_regex=r'^.*/label-([0-9]+)/.*$',
                label_word_net_id_regex=r'^.*/wordnet-([0-9]+)/.*$',
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='none',
                label_map=None
            )

    @staticmethod
    def test_closed_dataset_cannot_retrieve_sample(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly refuses to return a sample for a closed dataset.

        Parameters
        ----------
            image_directory_dataset_with_label_indices_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        image_directory_dataset.close()

        with pytest.raises(ValueError):
            image_directory_dataset.get_sample(0)

        with pytest.raises(ValueError):
            _ = image_directory_dataset[0]

    @staticmethod
    def test_cannot_retrieve_sample_for_out_of_bounds_index(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly raises an exception, when a sample is to be retrieved that is not in the
        dataset.

        Parameters
        ----------
            image_directory_dataset_with_label_indices_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )

        with pytest.raises(LookupError):
            image_directory_dataset.get_sample(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        with pytest.raises(LookupError):
            _ = image_directory_dataset[NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES]

    @staticmethod
    def test_sample_paths_file(
            image_directory_dataset_with_sample_paths_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can locate samples .

        Parameters
        ----------
            image_directory_dataset_with_sample_paths_file_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_sample_paths_file_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )

        # Only every second sample was added to the sample paths file, so the number of samples in the image directory
        # dataset should be only half of the number of images in the dataset directory
        number_of_images_in_dataset_directory = len(glob.glob(
            os.path.join(image_directory_dataset_with_sample_paths_file_path, '**/*.*'),
            recursive=True
        ))
        assert number_of_images_in_dataset_directory == NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES
        assert len(image_directory_dataset) == number_of_images_in_dataset_directory // 2

    @staticmethod
    def test_label_index_directory_name(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can properly parse the labels from directory that contain the index
        of the respective label.

        Parameters
        ----------
            image_directory_dataset_with_label_indices_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        image_directory_dataset.get_sample(0)

    @staticmethod
    def test_label_wordnet_id_directory_name(
            image_directory_dataset_with_wordnet_ids_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can properly parse the labels from directory that contain the index
        of the respective label.

        Parameters
        ----------
            image_directory_dataset_with_wordnet_ids_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_wordnet_ids_path,
            label_index_regex=None,
            label_word_net_id_regex=r'^.*/wordnet-([0-9]+)/.*$',
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        image_directory_dataset.get_sample(0)

    @staticmethod
    def test_label_cannot_be_determined(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the image directory dataset raises an exception, if it cannot determine the label of a sample,
        e.g., if the label index or WordNet ID RegEx's are incorrect.

        Parameters
        ----------
            image_directory_dataset_with_label_indices_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        with pytest.raises(LookupError):
            image_directory_dataset = ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=r'^.*/incorrect-([0-9]+)/.*$',
                label_word_net_id_regex=None,
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='none',
                label_map=label_map
            )
            image_directory_dataset.get_sample(0)

        with pytest.raises(LookupError):
            image_directory_dataset = ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=None,
                label_word_net_id_regex=r'^.*/incorrect-([0-9]+)/.*$',
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='none',
                label_map=label_map
            )
            image_directory_dataset.get_sample(0)

    @staticmethod
    def test_down_sampling_methods(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can properly down-sample the images to the correct input size,
        using all supported down-sampling methods.

        Parameters
        ----------
            image_directory_dataset_with_label_indices_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        # Checks if the dataset does nothing, when no down-sampling is specified, even if the images are too large
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=32,
            input_height=32,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        sample = image_directory_dataset.get_sample(0)
        assert sample.data.shape[0] == 64
        assert sample.data.shape[1] == 64

        # Checks all down-sampling methods
        for down_sampling_method in ['center_crop', 'resize']:
            image_directory_dataset = ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=r'^.*/label-([0-9]+)/.*$',
                label_word_net_id_regex=None,
                input_width=32,
                input_height=32,
                down_sampling_method=down_sampling_method,
                up_sampling_method='none',
                label_map=label_map
            )
            sample = image_directory_dataset.get_sample(0)
            assert sample.data.shape[0] == 32
            assert sample.data.shape[1] == 32

    @staticmethod
    def test_up_sampling_methods(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can properly up-sample the images to the correct input size,
        using all supported up-sampling methods.

        Parameters
        ----------
            image_directory_dataset_with_label_indices_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        # Checks if the dataset does nothing, when no up-sampling is specified, even if the images are too small
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=128,
            input_height=128,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        sample = image_directory_dataset.get_sample(0)
        assert sample.data.shape[0] == 64
        assert sample.data.shape[1] == 64

        # Checks all down-sampling methods
        up_sampling_methods = ['fill_zeros', 'fill_ones', 'edge_repeat', 'mirror_edge', 'wrap_around', 'resize']
        for up_sampling_method in up_sampling_methods:
            image_directory_dataset = ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=r'^.*/label-([0-9]+)/.*$',
                label_word_net_id_regex=None,
                input_width=128,
                input_height=128,
                down_sampling_method='none',
                up_sampling_method=up_sampling_method,
                label_map=label_map
            )
            sample = image_directory_dataset.get_sample(0)
            assert sample.data.shape[0] == 128
            assert sample.data.shape[1] == 128

    @staticmethod
    def test_retrieval_of_multiple_samples(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether multiple samples can be retrieved at the same time.

        Parameters
        ----------
            image_directory_dataset_with_label_indices_path: str
                The path to the image directory dataset that is used for the tests.
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=128,
            input_height=128,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )

        samples = image_directory_dataset[2:6]
        assert len(samples) == 4

        samples = image_directory_dataset[[2, 10, 12, 20, 19]]
        assert len(samples) == 5

        samples = image_directory_dataset[(8, 13, 27)]
        assert len(samples) == 3

        samples = image_directory_dataset[numpy.array([21, 4])]
        assert len(samples) == 2

        samples = image_directory_dataset[range(10)]
        assert len(samples) == 10


class TestSample:
    """Represents the tests for the Sample class."""

    @staticmethod
    def test_sample_creation() -> None:
        """Tests whether a sample can be created."""

        image = numpy.random.randint(256, size=(32, 32, 3), dtype=numpy.uint8)
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert numpy.array_equal(sample.data, image)
        assert sample.labels == [label]

    @staticmethod
    def test_sample_creation_with_multiple_labels() -> None:
        """Tests whether a sample can be created with multiple labels."""

        image = numpy.random.randint(256, size=(32, 32, 3), dtype=numpy.uint8)
        label_0 = Label(0, '00000000', 'Class 0')
        label_1 = Label(1, '00000001', 'Class 1')
        sample = Sample(0, image.copy(), [label_0, label_1])
        assert sample.index == 0
        assert numpy.array_equal(sample.data, image)
        assert sample.labels == [label_0, label_1]

    @staticmethod
    def test_sample_creation_with_pytorch_image() -> None:
        """Tests whether a sample can be created with an image that has the PyTorch channel order."""

        image = numpy.random.randint(256, size=(3, 32, 64), dtype=numpy.uint8)
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert sample.data.shape[0] == 32
        assert sample.data.shape[1] == 64
        assert sample.data.shape[2] == 3
        assert numpy.array_equal(sample.data, numpy.moveaxis(image, [0, 1, 2], [2, 0, 1]))
        assert sample.labels == [label]

    @staticmethod
    def test_sample_creation_with_float_image() -> None:
        """Tests whether a sample can be created with an image that has the float data type and pixel values between 0.0
        and 255.0.
        """

        image = numpy.random.randint(256, size=(32, 32, 3)).astype(dtype=numpy.float64)
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert numpy.array_equal(sample.data, image.astype(numpy.uint8))
        assert sample.labels == [label]

    @staticmethod
    def test_sample_creation_with_float_image_between_zero_and_one() -> None:
        """Tests whether a sample can be created with an image that has the float data type and pixel values between 0.0
        and 1.0.
        """

        image = numpy.random.uniform(low=0.0, high=1.0, size=(32, 32, 3))
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert numpy.array_equal(sample.data, (image * 255.0).astype(numpy.uint8))
        assert sample.labels == [label]

    @staticmethod
    def test_sample_creation_with_float_image_between_negative_one_and_one() -> None:
        """Tests whether a sample can be created with an image that has the float data type and pixel values between
        -1.0 and 1.0.
        """

        image = numpy.random.uniform(low=-1.0, high=1.0, size=(32, 32, 3))
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert numpy.array_equal(sample.data, ((image + 1) * (255.0 / 2.0)).astype(numpy.uint8))
        assert sample.labels == [label]


class TestLabelMap:
    """Represents the tests for the LabelMap class."""

    @staticmethod
    def test_labels_can_be_retrieved_via_index(label_map_file_path: str) -> None:
        """Tests whether labels can be retrieved via index from a label map.

        Parameters
        ----------
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        assert label_map.get_label_from_index(0) == 'Class 0'
        assert label_map.get_label_from_index(1) == 'Class 1'
        assert label_map.get_label_from_index(2) == 'Class 2'

        with pytest.raises(LookupError):
            label_map.get_label_from_index(3)

    @staticmethod
    def test_labels_can_be_retrieved_via_wordnet_id(label_map_file_path: str) -> None:
        """Tests whether labels can be retrieved via WordNet ID from a label map.

        Parameters
        ----------
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        assert label_map.get_label_from_word_net_id('00000000') == 'Class 0'
        assert label_map.get_label_from_word_net_id('00000001') == 'Class 1'
        assert label_map.get_label_from_word_net_id('00000002') == 'Class 2'

        with pytest.raises(LookupError):
            label_map.get_label_from_word_net_id("")

    @staticmethod
    def test_labels_can_be_retrieved_via_one_hot_vector(label_map_file_path: str) -> None:
        """Tests whether labels can be retrieved via one-hot vector from a label map.

        Parameters
        ----------
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        assert label_map.get_labels_from_n_hot_vector(numpy.array([1, 0, 0])) == ['Class 0']
        assert label_map.get_labels_from_n_hot_vector(numpy.array([0, 1, 0])) == ['Class 1']
        assert label_map.get_labels_from_n_hot_vector(numpy.array([0, 0, 1])) == ['Class 2']
        assert label_map.get_labels_from_n_hot_vector(numpy.array([1, 0, 1])) == ['Class 0', 'Class 2']
        assert label_map.get_labels_from_n_hot_vector(numpy.array([0, 1, 1])) == ['Class 1', 'Class 2']
        assert label_map.get_labels_from_n_hot_vector(numpy.array([1, 1, 0])) == ['Class 0', 'Class 1']
        assert label_map.get_labels_from_n_hot_vector(numpy.array([1, 1, 1])) == ['Class 0', 'Class 1', 'Class 2']

        with pytest.raises(LookupError):
            label_map.get_labels_from_n_hot_vector(numpy.array([0, 0, 0, 1]))

    @staticmethod
    def test_labels_can_be_retrieved_via_generic_retrieval_method(label_map_file_path: str) -> None:
        """Tests whether labels can be retrieved via the general retrieval method of the label map class.

        Parameters
        ----------
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        assert label_map.get_labels(numpy.array([0])[0]) == 'Class 0'
        assert label_map.get_labels(1) == 'Class 1'
        assert label_map.get_labels('00000002') == 'Class 2'
        assert label_map.get_labels(numpy.array([1, 1, 0])) == ['Class 0', 'Class 1']

        with pytest.raises(LookupError):
            label_map.get_labels([])


class TestLabel:
    """Represents the tests for the Label class."""

    @staticmethod
    def test_label_creation() -> None:
        """Tests whether a label can be created."""

        label = Label(0, '00000000', 'Class 0')
        assert label.index == 0
        assert label.word_net_id == '00000000'
        assert label.name == 'Class 0'


class TestWorkspace:
    """Represents the tests for the Workspace class."""

    @staticmethod
    def test_workspace_creation() -> None:
        """Tests whether a workspace can be created."""

        workspace = Workspace()
        assert not workspace.is_closed
        assert len(workspace.projects) == 0

    @staticmethod
    def test_workspace_can_be_closed_multiple_times() -> None:
        """Tests whether a workspace can be closed multiple times without raising an error."""

        workspace = Workspace()
        workspace.close()
        workspace.close()

    @staticmethod
    def test_project_can_be_added_to_workspace(project_file_path: str) -> None:
        """Tests whether a project can be added to a workspace.

        Parameters
        ----------
            project_file_path: str
                The path to the project file that is used in for the tests.
        """

        workspace = Workspace()
        workspace.add_project(project_file_path)

        assert len(workspace.projects) == 1
        assert workspace.get_project_names() == ['Test Project']
        assert workspace.get_project('Test Project').name == 'Test Project'

    @staticmethod
    def test_multiple_projects_can_be_added_to_workspace(project_file_path: str) -> None:
        """Tests whether multiple projects can be added to a workspace.

        Parameters
        ----------
            project_file_path: str
                The path to the project file that is used in for the tests.
        """

        workspace = Workspace()
        workspace.add_project(project_file_path)
        workspace.projects[0].name = 'Test Project 1'
        workspace.add_project(project_file_path)
        workspace.projects[1].name = 'Test Project 2'

        assert len(workspace.projects) == 2
        assert workspace.get_project_names() == ['Test Project 1', 'Test Project 2']
        assert workspace.get_project('Test Project 1').name == 'Test Project 1'
        assert workspace.get_project('Test Project 2').name == 'Test Project 2'

        workspace.close()
        for project in workspace.projects:
            assert project.is_closed

    @staticmethod
    def test_cannot_add_or_get_projects_of_closed_workspace() -> None:
        """Tests whether the workspace raises an error when adding or retrieving a project after the workspace was
        closed.
        """

        workspace = Workspace()
        workspace.close()

        with pytest.raises(ValueError):
            workspace.add_project('')

        with pytest.raises(ValueError):
            workspace.get_project('Test Project')

        with pytest.raises(ValueError):
            workspace.get_project_names()

    @staticmethod
    def test_workspace_cannot_find_unknown_project() -> None:
        """Tests whether a project can be added to a workspace."""

        workspace = Workspace()

        with pytest.raises(LookupError):
            workspace.get_project('Test Project')
