"""Contains the fixtures that are needed for the unit tests."""

import os
import json
import random
from typing import Iterator

import yaml
import h5py
import numpy
import pytest
from PIL import Image
from pytest import TempPathFactory
from flask import Flask
from flask.testing import FlaskClient

from virelay.server import Server
from virelay.model import Workspace

NUMBER_OF_CLASSES = 3
NUMBER_OF_SAMPLES = 40


@pytest.fixture(name='label_map_file_path', scope='session')
def get_label_map_file_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates a label map file.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the label file will be created.

    Returns:
        str: Returns the path to the created label map file.
    """

    label_map = [
        {
            'index': label_index,
            'word_net_id': f'{label_index:08d}',
            'name': f'Class {label_index:d}',
        } for label_index in range(NUMBER_OF_CLASSES)
    ]

    label_map_file_path = tmp_path_factory.getbasetemp() / 'label-map.json'
    with open(label_map_file_path, 'w', encoding='utf-8') as label_map_file:
        json.dump(label_map, label_map_file)

    return label_map_file_path.as_posix()


@pytest.fixture(name='hdf5_dataset_with_samples_as_hdf5_dataset_file_path', scope='session')
def get_hdf5_dataset_with_samples_as_hdf5_dataset_file_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an HDF5 dataset file, where the samples are stored in an HDF5 dataset.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the HDF5 dataset file will be created.

    Returns:
        str: Returns the path to the created input file.
    """

    data = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES, 3, 32, 32))
    data_labels = []
    for label_index in range(NUMBER_OF_CLASSES):
        data_labels.extend([label_index] * NUMBER_OF_SAMPLES)

    hdf5_dataset_with_samples_as_hdf5_dataset_file_path = tmp_path_factory.getbasetemp() / 'hdf5-dataset-with-samples-as-hdf5-dataset.h5'
    with h5py.File(hdf5_dataset_with_samples_as_hdf5_dataset_file_path, 'w') as dataset_file:
        dataset_file.create_dataset(
            'data',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, 3, 32, 32),
            dtype=numpy.float32,
            data=data
        )
        dataset_file.create_dataset(
            'label',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES,),
            dtype=numpy.uint16,
            data=numpy.array(data_labels)
        )

    return hdf5_dataset_with_samples_as_hdf5_dataset_file_path.as_posix()


@pytest.fixture(name='hdf5_dataset_with_samples_as_hdf5_group_file_path', scope='session')
def get_hdf5_dataset_with_samples_as_hdf5_group_file_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an HDF5 dataset file, where the samples are stored in an HDF5 group.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the HDF5 dataset file will be created.

    Returns:
        str: Returns the path to the created input file.
    """

    hdf5_dataset_with_samples_as_hdf5_group_file_path = tmp_path_factory.getbasetemp() / 'hdf5-dataset-with-samples-as-hdf5-group.h5'
    with h5py.File(hdf5_dataset_with_samples_as_hdf5_group_file_path, 'w') as dataset_file:
        dataset_file.create_group('data')
        dataset_file.create_group('label')

        for label_index in range(NUMBER_OF_CLASSES):
            for sample_index in range(NUMBER_OF_SAMPLES):
                dataset_file['data'].create_dataset(
                    f'sample-{sample_index}-label-{label_index}',
                    shape=(3, 32, 32),
                    dtype=numpy.float32,
                    data=numpy.random.uniform(0, 1, size=(3, 32, 32))
                )

                dataset_file['label'].create_dataset(
                    f'sample-{sample_index}-label-{label_index}',
                    shape=(),
                    dtype=numpy.uint16,
                    data=label_index
                )

    return hdf5_dataset_with_samples_as_hdf5_group_file_path.as_posix()


@pytest.fixture(name='hdf5_dataset_with_samples_as_hdf5_group_and_multiple_labels_file_path', scope='session')
def get_hdf5_dataset_with_samples_as_hdf5_group_and_multiple_labels_file_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an HDF5 dataset file, where the samples are stored in an HDF5 group.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the HDF5 dataset file will be created.

    Returns:
        str: Returns the path to the created input file.
    """

    hdf5_dataset_with_samples_as_hdf5_group_and_multiple_labels_file_path = \
        tmp_path_factory.getbasetemp() / 'hdf5-dataset-with-samples-as-hdf5-group-and-multiple-labels.h5'
    with h5py.File(hdf5_dataset_with_samples_as_hdf5_group_and_multiple_labels_file_path, 'w') as dataset_file:
        dataset_file.create_group('data')
        dataset_file.create_group('label')

        for label_index in range(NUMBER_OF_CLASSES):
            for sample_index in range(NUMBER_OF_SAMPLES):
                dataset_file['data'].create_dataset(
                    f'sample-{sample_index}-label-{label_index}',
                    shape=(3, 32, 32),
                    dtype=numpy.float32,
                    data=numpy.random.uniform(0, 1, size=(3, 32, 32))
                )

                labels = [False] * NUMBER_OF_CLASSES
                labels[label_index] = True
                labels[(label_index + 1) % NUMBER_OF_CLASSES] = True

                dataset_file['label'].create_dataset(
                    f'sample-{sample_index}-label-{label_index}',
                    shape=(NUMBER_OF_CLASSES,),
                    dtype=numpy.bool,
                    data=numpy.array(labels, dtype=numpy.bool)
                )

    return hdf5_dataset_with_samples_as_hdf5_group_and_multiple_labels_file_path.as_posix()


@pytest.fixture(name='image_directory_dataset_with_label_indices_path', scope='session')
def get_image_directory_dataset_with_label_indices_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an image dataset, where the image files are in a directory hierarchy were the names of the directories represent
    the labels of the images. In this version of the fixture, the label directories have the index of the label in them.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the image directory dataset will be created.

    Returns:
        str: Returns the path to the created image dataset.
    """

    image_directory_dataset_path = tmp_path_factory.getbasetemp() / 'image-dataset-with-label-indices'
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


@pytest.fixture(name='image_directory_dataset_with_wordnet_ids_path', scope='session')
def get_image_directory_dataset_with_wordnet_ids_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an image dataset, where the image files are in a directory hierarchy were the names of the directories represent
    the labels of the images. In this version of the fixture, the label directories have the WordNet ID of the label in them.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the image directory dataset will be created.

    Returns:
        str: Returns the path to the created image dataset.
    """

    image_directory_dataset_path = tmp_path_factory.getbasetemp() / 'image-dataset-with-wordnet-ids'
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


@pytest.fixture(name='image_directory_dataset_with_sample_paths_file_path', scope='session')
def get_image_directory_dataset_with_sample_paths_file_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an image dataset, where the image files are in a directory hierarchy were the names of the directories represent
    the labels of the images. In this version of the fixture, a file exists, which lists all samples of the dataset. Only every second image is
    actually added to the sample paths file, so that it can be validated that the dataset actually loaded the samples from the sample paths file.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the image directory dataset will be created.

    Returns:
        str: Returns the path to the created image dataset.
    """

    image_directory_dataset_path = tmp_path_factory.getbasetemp() / 'image-dataset-with-sample-paths-file'
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


@pytest.fixture(name='attribution_with_attributions_as_hdf5_dataset_file_path', scope='session')
def get_attribution_with_attributions_as_hdf5_dataset_file_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an attribution file, where the attributions are stored in an HDF5 dataset.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the attribution file will be created.

    Returns:
        str: Returns the path to the created attribution file.
    """

    attributions = numpy.random.uniform(-1, 1, size=(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES, 3, 32, 32))
    predictions = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES, NUMBER_OF_CLASSES))
    data_labels = []
    for label_index in range(NUMBER_OF_CLASSES):
        data_labels.extend([label_index] * NUMBER_OF_SAMPLES)

    attribution_with_attributions_as_hdf5_dataset_file_path = tmp_path_factory.getbasetemp() / 'attributions.h5'
    with h5py.File(attribution_with_attributions_as_hdf5_dataset_file_path, 'w') as attribution_file:
        attribution_file.create_dataset(
            'attribution',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, 3, 32, 32),
            dtype=numpy.float32,
            data=attributions
        )
        attribution_file.create_dataset(
            'prediction',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, NUMBER_OF_CLASSES),
            dtype=numpy.float32,
            data=predictions
        )
        attribution_file.create_dataset(
            'label',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES,),
            dtype=numpy.uint16,
            data=numpy.array(data_labels)
        )

    return attribution_with_attributions_as_hdf5_dataset_file_path.as_posix()


@pytest.fixture(name='attribution_with_attributions_as_hdf5_group_file_path', scope='session')
def get_attribution_with_attributions_as_hdf5_group_file_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an attribution file, where the attributions are stored in an HDF5 group.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the attribution file will be created.

    Returns:
        str: Returns the path to the created attribution file.
    """

    attribution_with_attributions_as_hdf5_group_file_path = tmp_path_factory.getbasetemp() / 'attributions.h5'
    with h5py.File(attribution_with_attributions_as_hdf5_group_file_path, 'w') as attribution_file:
        attribution_file.create_group('attribution')
        attribution_file.create_group('prediction')
        attribution_file.create_group('label')

        for label_index in range(NUMBER_OF_CLASSES):
            for sample_index in range(NUMBER_OF_SAMPLES):
                attribution_file['attribution'].create_dataset(
                    f'attribution-{sample_index}-label-{label_index}',
                    shape=(3, 32, 32),
                    dtype=numpy.float32,
                    data=numpy.random.uniform(-1, 1, size=(3, 32, 32))
                )

                attribution_file['prediction'].create_dataset(
                    f'attribution-{sample_index}-label-{label_index}',
                    shape=(NUMBER_OF_CLASSES,),
                    dtype=numpy.float32,
                    data=numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES,))
                )

                attribution_file['label'].create_dataset(
                    f'attribution-{sample_index}-label-{label_index}',
                    shape=(),
                    dtype=numpy.uint16,
                    data=label_index
                )

    return attribution_with_attributions_as_hdf5_group_file_path.as_posix()


@pytest.fixture(name='attribution_file_with_sample_indices_path', scope='session')
def get_attribution_file_with_sample_indices_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an attribution file, where the indices of the samples for which attributions are available is in a separate
    dataset.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the attribution file will be created.

    Returns:
        str: Returns the path to the created attribution file.
    """

    attributions = None
    predictions = None
    data_labels = None
    attribution_file_with_sample_indices_path = tmp_path_factory.getbasetemp() / 'attributions-with-sample-indices.h5'
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

    with h5py.File(attribution_file_with_sample_indices_path, 'w') as attribution_file:
        attribution_file.create_dataset(
            'index',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES,),
            dtype=numpy.uint32,
            data=numpy.arange(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, dtype=numpy.uint32)
        )
        attribution_file.create_dataset(
            'attribution',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, 3, 32, 32),
            dtype=numpy.float32,
            data=attributions
        )
        attribution_file.create_dataset(
            'prediction',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES, NUMBER_OF_CLASSES),
            dtype=numpy.float32,
            data=predictions
        )
        attribution_file.create_dataset(
            'label',
            shape=(NUMBER_OF_SAMPLES * NUMBER_OF_CLASSES,),
            dtype=numpy.uint16,
            data=data_labels
        )

    return attribution_file_with_sample_indices_path.as_posix()


@pytest.fixture(name='spectral_analysis_file_path', scope='session')
def get_spectral_analysis_file_path_fixture(
    tmp_path_factory: TempPathFactory,
    attribution_with_attributions_as_hdf5_dataset_file_path: str,
    label_map_file_path: str
) -> str:
    """A test fixture, which creates an analysis file that contains a spectral analysis.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the analysis file will be created.
        attribution_with_attributions_as_hdf5_dataset_file_path (str): The path to the attribution file that contains the attributions for which the
            analysis is to be generated.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created analysis file.
    """

    spectral_analysis_file_path = tmp_path_factory.getbasetemp() / 'spectral-analysis.h5'

    with open(label_map_file_path, 'r', encoding='utf-8') as label_map_file:
        label_map = json.load(label_map_file)
    label_map = {element['index']: element['word_net_id'] for element in label_map}

    number_of_clusters_to_try = [2, 3]
    with h5py.File(attribution_with_attributions_as_hdf5_dataset_file_path, 'r') as attribution_file:
        with h5py.File(spectral_analysis_file_path, 'w') as analysis_file:

            data_labels = attribution_file['label'][:]

            for label_index in [int(element) for element in label_map]:
                index, = numpy.nonzero(data_labels == label_index)

                eigenvalues = numpy.random.uniform(size=(32,)).astype(numpy.float32)
                embedding = numpy.random.normal(size=(NUMBER_OF_SAMPLES, 32)).astype(numpy.float32)
                kmeans = (numpy.random.randint(
                    number_of_clusters,
                    size=(NUMBER_OF_SAMPLES,),
                    dtype=numpy.int32
                ) for number_of_clusters in number_of_clusters_to_try)
                dbscan = (numpy.random.randint(
                    low=-1,
                    high=1,
                    size=(NUMBER_OF_SAMPLES,),
                    dtype=numpy.int32
                ) for _ in number_of_clusters_to_try)
                hdbscan = numpy.random.randint(
                    low=-1,
                    high=1,
                    size=(NUMBER_OF_SAMPLES,),
                    dtype=numpy.int32
                )
                agglomerative = (numpy.random.randint(
                    number_of_clusters,
                    size=(NUMBER_OF_SAMPLES,),
                    dtype=numpy.int32
                ) for number_of_clusters in number_of_clusters_to_try)
                umap = numpy.random.uniform(
                    high=10.0,
                    size=(NUMBER_OF_SAMPLES, len(number_of_clusters_to_try))
                ).astype(numpy.float32)
                tsne = numpy.random.normal(
                    scale=50.0,
                    size=(NUMBER_OF_SAMPLES, len(number_of_clusters_to_try))
                ).astype(numpy.float32)

                analysis_name = label_map.get(label_index, f'{label_index:03d}')
                analysis_group = analysis_file.require_group(analysis_name)
                analysis_group['index'] = index.astype(numpy.uint32)

                embedding_group = analysis_group.require_group('embedding')
                embedding_group['spectral'] = embedding
                embedding_group['spectral'].attrs['eigenvalue'] = eigenvalues

                embedding_group['tsne'] = tsne
                embedding_group['tsne'].attrs['embedding'] = 'spectral'
                embedding_group['tsne'].attrs['index'] = numpy.array([0, 1])

                embedding_group['umap'] = umap
                embedding_group['umap'].attrs['embedding'] = 'spectral'
                embedding_group['umap'].attrs['index'] = numpy.array([0, 1])

                cluster_group = analysis_group.require_group('cluster')
                for number_of_clusters, clustering in zip(number_of_clusters_to_try, kmeans):
                    cluster_id = f'kmeans-{number_of_clusters:02d}'
                    cluster_group[cluster_id] = clustering
                    cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                    cluster_group[cluster_id].attrs['k'] = number_of_clusters
                    cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype=numpy.uint32)

                for number_of_clusters, clustering in zip(number_of_clusters_to_try, dbscan):
                    cluster_id = f'dbscan-eps={number_of_clusters / 10.0:.1f}'
                    cluster_group[cluster_id] = clustering
                    cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                    cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype=numpy.uint32)

                cluster_id = 'hdbscan'
                cluster_group[cluster_id] = hdbscan
                cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype=numpy.uint32)

                for number_of_clusters, clustering in zip(number_of_clusters_to_try, agglomerative):
                    cluster_id = f'agglomerative-{number_of_clusters:02d}'
                    cluster_group[cluster_id] = clustering
                    cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                    cluster_group[cluster_id].attrs['k'] = number_of_clusters
                    cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype=numpy.uint32)

    return spectral_analysis_file_path.as_posix()


@pytest.fixture(name='spectral_analysis_file_without_eigenvalues_path', scope='session')
def get_spectral_analysis_file_without_eigenvalues_path_fixture(
    tmp_path_factory: TempPathFactory,
    attribution_with_attributions_as_hdf5_dataset_file_path: str,
    label_map_file_path: str
) -> str:
    """A test fixture, which creates an analysis file that contains a spectral analysis, but without eigenvalues.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the analysis file will be created.
        attribution_with_attributions_as_hdf5_dataset_file_path (str): The path to the attribution file that contains the attributions for which the
            analysis is to be generated.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created analysis file.
    """

    spectral_analysis_file_without_eigenvalues_path = \
        tmp_path_factory.getbasetemp() / 'spectral-analysis-without-eigenvalues.h5'

    with open(label_map_file_path, 'r', encoding='utf-8') as label_map_file:
        label_map = json.load(label_map_file)
    label_map = {element['index']: element['word_net_id'] for element in label_map}

    number_of_clusters_to_try = [2, 3]
    with h5py.File(attribution_with_attributions_as_hdf5_dataset_file_path, 'r') as attribution_file:
        with h5py.File(spectral_analysis_file_without_eigenvalues_path, 'w') as analysis_file:

            labels: h5py.Dataset | h5py.Group = attribution_file['label']
            if isinstance(labels, h5py.Dataset):
                data_labels = labels[:]
            else:
                data_labels = numpy.array([label[()] for label in labels.values()])
            print(type(data_labels))

            for label_index in [int(element) for element in label_map]:
                index, = numpy.nonzero(data_labels == label_index)

                embedding = numpy.random.normal(size=(NUMBER_OF_SAMPLES, 32)).astype(numpy.float32)
                kmeans = (numpy.random.randint(
                    number_of_clusters,
                    size=(NUMBER_OF_SAMPLES,),
                    dtype=numpy.int32
                ) for number_of_clusters in number_of_clusters_to_try)
                dbscan = (numpy.random.randint(
                    low=-1,
                    high=1,
                    size=(NUMBER_OF_SAMPLES,),
                    dtype=numpy.int32
                ) for _ in number_of_clusters_to_try)
                hdbscan = numpy.random.randint(
                    low=-1,
                    high=1,
                    size=(NUMBER_OF_SAMPLES,),
                    dtype=numpy.int32
                )
                agglomerative = (numpy.random.randint(
                    number_of_clusters,
                    size=(NUMBER_OF_SAMPLES,),
                    dtype=numpy.int32
                ) for number_of_clusters in number_of_clusters_to_try)
                umap = numpy.random.uniform(
                    high=10.0,
                    size=(NUMBER_OF_SAMPLES, len(number_of_clusters_to_try))
                ).astype(numpy.float32)
                tsne = numpy.random.normal(
                    scale=50.0,
                    size=(NUMBER_OF_SAMPLES, len(number_of_clusters_to_try))
                ).astype(numpy.float32)

                analysis_name = label_map.get(label_index, f'{label_index:03d}')
                analysis_group = analysis_file.require_group(analysis_name)
                analysis_group['index'] = index.astype(numpy.uint32)

                embedding_group = analysis_group.require_group('embedding')
                embedding_group['spectral'] = embedding

                embedding_group['tsne'] = tsne
                embedding_group['tsne'].attrs['embedding'] = 'spectral'
                embedding_group['tsne'].attrs['index'] = numpy.array([0, 1])

                embedding_group['umap'] = umap
                embedding_group['umap'].attrs['embedding'] = 'spectral'
                embedding_group['umap'].attrs['index'] = numpy.array([0, 1])

                cluster_group = analysis_group.require_group('cluster')
                for number_of_clusters, clustering in zip(number_of_clusters_to_try, kmeans):
                    cluster_id = f'kmeans-{number_of_clusters:02d}'
                    cluster_group[cluster_id] = clustering
                    cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                    cluster_group[cluster_id].attrs['k'] = number_of_clusters
                    cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype=numpy.uint32)

                for number_of_clusters, clustering in zip(number_of_clusters_to_try, dbscan):
                    cluster_id = f'dbscan-eps={number_of_clusters / 10.0:.1f}'
                    cluster_group[cluster_id] = clustering
                    cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                    cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype=numpy.uint32)

                cluster_id = 'hdbscan'
                cluster_group[cluster_id] = hdbscan
                cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype=numpy.uint32)

                for number_of_clusters, clustering in zip(number_of_clusters_to_try, agglomerative):
                    cluster_id = f'agglomerative-{number_of_clusters:02d}'
                    cluster_group[cluster_id] = clustering
                    cluster_group[cluster_id].attrs['embedding'] = 'spectral'
                    cluster_group[cluster_id].attrs['k'] = number_of_clusters
                    cluster_group[cluster_id].attrs['index'] = numpy.arange(embedding.shape[1], dtype=numpy.uint32)

    return spectral_analysis_file_without_eigenvalues_path.as_posix()


@pytest.fixture(name='project_file_with_hdf5_dataset_path', scope='session')
def get_project_file_with_hdf5_dataset_path_fixture(
        tmp_path_factory: TempPathFactory,
        hdf5_dataset_with_samples_as_hdf5_dataset_file_path: str,
        attribution_with_attributions_as_hdf5_dataset_file_path: str,
        spectral_analysis_file_path: str,
        label_map_file_path: str) -> str:
    """A test fixture, which creates an project file with an HDF5 dataset.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the project file will be created.
        hdf5_dataset_with_samples_as_hdf5_dataset_file_path (str): The path to the HDF5 dataset file.
        attribution_with_attributions_as_hdf5_dataset_file_path (str): The path to the attribution file.
        spectral_analysis_file_path (str): The path to the spectral analysis file.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created project file.
    """

    project_file_with_hdf5_dataset_path = tmp_path_factory.getbasetemp() / 'project-with-hdf5-dataset.yaml'

    project = {
        'project': {
            'name': 'Test Project',
            'model': 'No Model',
            'label_map': os.path.relpath(label_map_file_path, start=tmp_path_factory.getbasetemp().as_posix()),
            'dataset': {
                'name': "HDF5 Dataset",
                'type': 'hdf5',
                'path': os.path.relpath(hdf5_dataset_with_samples_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())
            },
            'attributions': {
                'attribution_method': 'Random Attribution',
                'attribution_strategy': 'true_label',
                'sources': [os.path.relpath(attribution_with_attributions_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())]
            },
            'analyses': [
                {
                    'analysis_method': 'Spectral Analysis',
                    'sources': [os.path.relpath(
                        spectral_analysis_file_path,
                        start=tmp_path_factory.getbasetemp().as_posix()
                    )]
                }
            ]
        }
    }

    with open(project_file_with_hdf5_dataset_path, 'w', encoding='utf-8') as project_file:
        yaml.dump(project, project_file, default_flow_style=False)

    return project_file_with_hdf5_dataset_path.as_posix()


@pytest.fixture(name='project_file_without_eigenvalues_in_analysis_database_path', scope='session')
def get_project_file_without_eigenvalues_in_analysis_database_path_fixture(
    tmp_path_factory: TempPathFactory,
    hdf5_dataset_with_samples_as_hdf5_dataset_file_path: str,
    attribution_with_attributions_as_hdf5_dataset_file_path: str,
    spectral_analysis_file_without_eigenvalues_path: str,
    label_map_file_path: str
) -> str:
    """A test fixture, which creates an project file where the analysis database does not contain eigenvalues.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the project file will be created.
        hdf5_dataset_with_samples_as_hdf5_dataset_file_path (str): The path to the HDF5 dataset file.
        attribution_with_attributions_as_hdf5_dataset_file_path (str): The path to the attribution file.
        spectral_analysis_file_without_eigenvalues_path (str): The path to the spectral analysis file.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created project file.
    """

    project_file_without_eigenvalues_in_analysis_database_path = \
        tmp_path_factory.getbasetemp() / 'project-without-eigenvalues-in-analysis-database.yaml'

    project = {
        'project': {
            'name': 'Test Project',
            'model': 'No Model',
            'label_map': os.path.relpath(label_map_file_path, start=tmp_path_factory.getbasetemp().as_posix()),
            'dataset': {
                'name': "HDF5 Dataset",
                'type': 'hdf5',
                'path': os.path.relpath(hdf5_dataset_with_samples_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())
            },
            'attributions': {
                'attribution_method': 'Random Attribution',
                'attribution_strategy': 'true_label',
                'sources': [os.path.relpath(attribution_with_attributions_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())]
            },
            'analyses': [
                {
                    'analysis_method': 'Spectral Analysis',
                    'sources': [os.path.relpath(
                        spectral_analysis_file_without_eigenvalues_path,
                        start=tmp_path_factory.getbasetemp().as_posix()
                    )]
                }
            ]
        }
    }

    with open(project_file_without_eigenvalues_in_analysis_database_path, 'w', encoding='utf-8') as project_file:
        yaml.dump(project, project_file, default_flow_style=False)

    return project_file_without_eigenvalues_in_analysis_database_path.as_posix()


@pytest.fixture(name='project_file_with_image_directory_dataset_path', scope='session')
def get_project_file_with_image_directory_dataset_path_fixture(
    tmp_path_factory: TempPathFactory,
    image_directory_dataset_with_label_indices_path: str,
    attribution_with_attributions_as_hdf5_dataset_file_path: str,
    spectral_analysis_file_path: str,
    label_map_file_path: str
) -> str:
    """A test fixture, which creates an project file with an image directory dataset.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the project file will be created.
        image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset file.
        attribution_with_attributions_as_hdf5_dataset_file_path (str): The path to the attribution file.
        spectral_analysis_file_path (str): The path to the analysis file.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created project file.
    """

    project_file_with_image_directory_dataset_path = tmp_path_factory.getbasetemp() / 'project-with-image-directory-dataset.yaml'

    project = {
        'project': {
            'name': 'Test Project',
            'model': 'No Model',
            'label_map': os.path.relpath(label_map_file_path, start=tmp_path_factory.getbasetemp().as_posix()),
            'dataset': {
                'name': "Image Directory Dataset",
                'type': 'image_directory',
                'path': os.path.relpath(
                    image_directory_dataset_with_label_indices_path,
                    start=tmp_path_factory.getbasetemp().as_posix()
                ),
                'label_index_regex': r'^.*/label-([0-9]+)/.*$',
                'label_word_net_id_regex': None,
                'input_width': 64,
                'input_height': 64,
                'down_sampling_method': 'none',
                'up_sampling_method': 'none'
            },
            'attributions': {
                'attribution_method': 'Random Attribution',
                'attribution_strategy': 'true_label',
                'sources': [os.path.relpath(attribution_with_attributions_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())]
            },
            'analyses': [
                {
                    'analysis_method': 'Spectral Analysis',
                    'sources': [os.path.relpath(
                        spectral_analysis_file_path,
                        start=tmp_path_factory.getbasetemp().as_posix()
                    )]
                }
            ]
        }
    }

    with open(project_file_with_image_directory_dataset_path, 'w', encoding='utf-8') as project_file:
        yaml.dump(project, project_file, default_flow_style=False)

    return project_file_with_image_directory_dataset_path.as_posix()


@pytest.fixture(name='project_file_with_multiple_analysis_databases_path', scope='session')
def get_project_file_with_multiple_analysis_databases_path_fixture(
    tmp_path_factory: TempPathFactory,
    hdf5_dataset_with_samples_as_hdf5_dataset_file_path: str,
    attribution_with_attributions_as_hdf5_dataset_file_path: str,
    spectral_analysis_file_path: str,
    label_map_file_path: str
) -> str:
    """A test fixture, which creates an project file with multiple analysis databases.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the project file will be created.
        hdf5_dataset_with_samples_as_hdf5_dataset_file_path (str): The path to the HDF5 dataset file.
        attribution_with_attributions_as_hdf5_dataset_file_path (str): The path to the attribution file.
        spectral_analysis_file_path (str): The path to the spectral analysis file.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created project file.
    """

    project_file_with_multiple_analysis_databases_path = \
        tmp_path_factory.getbasetemp() / 'project-with-multiple-analysis-databases.yaml'

    project = {
        'project': {
            'name': 'Test Project',
            'model': 'No Model',
            'label_map': os.path.relpath(label_map_file_path, start=tmp_path_factory.getbasetemp().as_posix()),
            'dataset': {
                'name': "HDF5 Dataset",
                'type': 'hdf5',
                'path': os.path.relpath(hdf5_dataset_with_samples_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())
            },
            'attributions': {
                'attribution_method': 'Random Attribution',
                'attribution_strategy': 'true_label',
                'sources': [os.path.relpath(attribution_with_attributions_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())]
            },
            'analyses': [
                {
                    'analysis_method': 'Spectral Analysis',
                    'sources': [os.path.relpath(
                        spectral_analysis_file_path,
                        start=tmp_path_factory.getbasetemp().as_posix()
                    )]
                },
                {
                    'analysis_method': 'Spectral Analysis',
                    'sources': [os.path.relpath(
                        spectral_analysis_file_path,
                        start=tmp_path_factory.getbasetemp().as_posix()
                    )]
                }
            ]
        }
    }

    with open(project_file_with_multiple_analysis_databases_path, 'w', encoding='utf-8') as project_file:
        yaml.dump(project, project_file, default_flow_style=False)

    return project_file_with_multiple_analysis_databases_path.as_posix()


@pytest.fixture(name='project_file_without_attributions_or_analyses_path', scope='session')
def get_project_file_without_attributions_or_analyses_path_fixture(
    tmp_path_factory: TempPathFactory,
    hdf5_dataset_with_samples_as_hdf5_dataset_file_path: str,
    label_map_file_path: str
) -> str:
    """A test fixture, which creates an project file without attributions or analyses.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the project file will be created.
        hdf5_dataset_with_samples_as_hdf5_dataset_file_path (str): The path to the HDF5 dataset file.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created project file.
    """

    project_file_without_attributions_or_analyses_path = \
        tmp_path_factory.getbasetemp() / 'project-without-attributions-or-analyses.yaml'

    project = {
        'project': {
            'name': 'Test Project',
            'model': 'No Model',
            'label_map': os.path.relpath(label_map_file_path, start=tmp_path_factory.getbasetemp().as_posix()),
            'dataset': {
                'name': "HDF5 Dataset",
                'type': 'hdf5',
                'path': os.path.relpath(hdf5_dataset_with_samples_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())
            }
        }
    }

    with open(project_file_without_attributions_or_analyses_path, 'w', encoding='utf-8') as project_file:
        yaml.dump(project, project_file, default_flow_style=False)

    return project_file_without_attributions_or_analyses_path.as_posix()


@pytest.fixture(name='project_file_with_unknown_dataset_type_path', scope='session')
def get_project_file_with_unknown_dataset_type_path_fixture(
    tmp_path_factory: TempPathFactory,
    attribution_with_attributions_as_hdf5_dataset_file_path: str,
    spectral_analysis_file_path: str,
    label_map_file_path: str
) -> str:
    """A test fixture, which creates an project file with an unknown dataset type.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the project file will be created.
        attribution_with_attributions_as_hdf5_dataset_file_path (str): The path to the attribution file.
        spectral_analysis_file_path (str): The path to the analysis file.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created project file.
    """

    project_file_with_unknown_dataset_type_path = \
        tmp_path_factory.getbasetemp() / 'project-with-unknown-dataset-type.yaml'

    project = {
        'project': {
            'name': 'Test Project',
            'model': 'No Model',
            'label_map': os.path.relpath(label_map_file_path, start=tmp_path_factory.getbasetemp().as_posix()),
            'dataset': {
                'type': 'unknown_dataset_type'
            },
            'attributions': {
                'attribution_method': 'Random Attribution',
                'attribution_strategy': 'true_label',
                'sources': [os.path.relpath(attribution_with_attributions_as_hdf5_dataset_file_path, start=tmp_path_factory.getbasetemp().as_posix())]
            },
            'analyses': [
                {
                    'analysis_method': 'Spectral Analysis',
                    'sources': [os.path.relpath(
                        spectral_analysis_file_path,
                        start=tmp_path_factory.getbasetemp().as_posix()
                    )]
                }
            ]
        }
    }

    with open(project_file_with_unknown_dataset_type_path, 'w', encoding='utf-8') as project_file:
        yaml.dump(project, project_file, default_flow_style=False)

    return project_file_with_unknown_dataset_type_path.as_posix()


@pytest.fixture(name='project_file_without_dataset_path', scope='session')
def get_project_file_without_dataset_path_fixture(
    tmp_path_factory: TempPathFactory,
    attribution_with_attributions_as_hdf5_dataset_file_path: str,
    spectral_analysis_file_path: str,
    label_map_file_path: str
) -> str:
    """A test fixture, which creates an project file without dataset.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the project file will be created.
        attribution_with_attributions_as_hdf5_dataset_file_path (str): The path to the attribution file.
        spectral_analysis_file_path (str): The path to the analysis file.
        label_map_file_path (str): The path to the label map file.

    Returns:
        str: Returns the path to the created project file.
    """

    project_file_without_dataset_path = tmp_path_factory.getbasetemp() / 'project-without-dataset.yaml'

    project = {
        'project': {
            'name': 'Test Project',
            'model': 'No Model',
            'label_map': os.path.relpath(label_map_file_path, start=tmp_path_factory.getbasetemp().as_posix()),
            'attributions': {
                'attribution_method': 'Random Attribution',
                'attribution_strategy': 'true_label',
                'sources': [os.path.relpath(
                    attribution_with_attributions_as_hdf5_dataset_file_path,
                    start=tmp_path_factory.getbasetemp().as_posix()
                )],
            },
            'analyses': [
                {
                    'analysis_method': 'Spectral Analysis',
                    'sources': [os.path.relpath(
                        spectral_analysis_file_path,
                        start=tmp_path_factory.getbasetemp().as_posix()
                    )]
                }
            ]
        }
    }

    with open(project_file_without_dataset_path, 'w', encoding='utf-8') as project_file:
        yaml.dump(project, project_file, default_flow_style=False)

    return project_file_without_dataset_path.as_posix()


@pytest.fixture(name='broken_project_file_path', scope='session')
def get_broken_project_file_path_fixture(tmp_path_factory: TempPathFactory) -> str:
    """A test fixture, which creates an project file, which is an invalid YAML file.

    Args:
        tmp_path_factory (TempPathFactory): A factory for creating a temporary directory in which the project file will be created.

    Returns:
        str: Returns the path to the created project file.
    """

    broken_project_file_path = tmp_path_factory.getbasetemp() / 'broken-project.yaml'

    with open(broken_project_file_path, 'w', encoding='utf-8') as project_file:
        project_file.write('unbalanced brackets: ][')

    return broken_project_file_path.as_posix()


@pytest.fixture(name='app')
def get_app_fixture(project_file_with_hdf5_dataset_path: str) -> Iterator[Flask]:
    """A test fixture, which creates a ViRelAy server and returns corresponding Flask app.

    Args:
        project_file_with_hdf5_dataset_path (str): The path to the project file that is used in for the tests.

    Yields:
        Flask: Yields the Flask app for the ViRelAy server.
    """

    workspace = Workspace()
    workspace.add_project(project_file_with_hdf5_dataset_path)
    server = Server(workspace)
    server.app.config['TESTING'] = True
    yield server.app
    workspace.close()


@pytest.fixture(name='app_without_eigenvalues_in_analysis_database')
def get_app_without_eigenvalues_in_analysis_database_fixture(project_file_without_eigenvalues_in_analysis_database_path: str) -> Iterator[Flask]:
    """A test fixture, which creates a ViRelAy server and returns corresponding Flask app.

    Args:
        project_file_without_eigenvalues_in_analysis_database_path (str): The path to the project file that is used in for the tests.

    Yields:
        Flask: Yields the Flask app for the ViRelAy server.
    """

    workspace = Workspace()
    workspace.add_project(project_file_without_eigenvalues_in_analysis_database_path)
    server = Server(workspace)
    server.app.config['TESTING'] = True
    yield server.app
    workspace.close()


@pytest.fixture(name='app_with_empty_workspace')
def get_app_with_empty_workspace_fixture() -> Iterator[Flask]:
    """A test fixture, which creates a ViRelAy server for an empty workspace and returns corresponding Flask app.

    Yields:
        Flask: Yields the Flask app for the ViRelAy server.
    """

    workspace = Workspace()
    server = Server(workspace)
    server.app.config['TESTING'] = True
    yield server.app
    workspace.close()


@pytest.fixture(name='app_in_debug_mode')
def get_app_in_debug_mode_fixture() -> Iterator[Flask]:
    """A test fixture, which creates a ViRelAy server in debug mode and returns corresponding Flask app.

    Yields:
        Flask: Yields the Flask app for the ViRelAy server.
    """

    workspace = Workspace()
    server = Server(workspace, is_in_debug_mode=True)
    server.app.config['TESTING'] = True
    yield server.app
    workspace.close()


@pytest.fixture(name='test_client')
def get_test_client_fixture(app: Flask) -> FlaskClient:
    """Creates a test HTTP client for a Flask app that hosts a ViRelAy server.

    Args:
        app (Flask): The Flask application for which the test client is to be created.

    Returns:
        FlaskClient: Returns the created test HTTP client for the Flask application
    """

    return app.test_client()


@pytest.fixture(name='test_client_without_eigenvalues_in_analysis')
def get_test_client_without_eigenvalues_in_analysis_fixture(app_without_eigenvalues_in_analysis_database: Flask) -> FlaskClient:
    """Creates a test HTTP client for a Flask app that hosts a ViRelAy server.

    Args:
        app_without_eigenvalues_in_analysis_database (Flask): The Flask application for which the test client is to be
            created.

    Returns:
        FlaskClient: Returns the created test HTTP client for the Flask application
    """

    return app_without_eigenvalues_in_analysis_database.test_client()


@pytest.fixture(name='test_client_with_app_in_debug_model')
def get_test_client_with_app_in_debug_model_fixture(app_in_debug_mode: Flask) -> FlaskClient:
    """Creates a test HTTP client for a Flask app that hosts a ViRelAy server that is in debug mode.

    Args:
        app_in_debug_mode (Flask): The Flask application for which the test client is to be created.

    Returns:
        FlaskClient: Returns the created test HTTP client for the Flask application
    """

    return app_in_debug_mode.test_client()
