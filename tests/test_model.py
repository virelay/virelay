"""Contains the tests for the model abstractions of ViRelAy"""

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

from virelay.model import ImageDirectoryDataset, LabelMap
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

    input_file_path = tmp_path / 'input.h5'
    for label_index in range(NUMBER_OF_CLASSES):

        data = numpy.random.uniform(0, 1, size=(NUMBER_OF_SAMPLES, 3, 32, 32))
        data_labels = numpy.array([label_index] * NUMBER_OF_SAMPLES)

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
    for label_index in range(NUMBER_OF_CLASSES):

        attributions = numpy.random.uniform(-1, 1, size=(NUMBER_OF_SAMPLES, 3, 32, 32))
        predictions = numpy.random.uniform(0, 1, size=(NUMBER_OF_SAMPLES, NUMBER_OF_CLASSES))
        data_labels = numpy.array([label_index] * NUMBER_OF_SAMPLES)

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


class TestImageDirectoryDataset:
    """Represents the tests for the ImageDirectoryDataset class."""

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
            image_directory_dataset_with_sample_paths_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly refuses to return a sample for a closed dataset.

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
        image_directory_dataset.close()

        with pytest.raises(ValueError):
            image_directory_dataset.get_sample(0)

        with pytest.raises(ValueError):
            image_directory_dataset[0]

    @staticmethod
    def test_cannot_retrieve_sample_for_out_of_bounds_index(
            image_directory_dataset_with_sample_paths_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly raises an exception, when a sample is to be retrieved that is not in the
        dataset.

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

        with pytest.raises(LookupError):
            image_directory_dataset.get_sample(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        with pytest.raises(LookupError):
            image_directory_dataset[NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES]

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
