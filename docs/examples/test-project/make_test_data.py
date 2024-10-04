"""Generates a random dataset and random attributions for this dataset, which can then be used to generate a meta-analysis and ultimately a test
project for ViRelAy.
"""

import os
import json
import argparse

import h5py
import numpy
from numpy.typing import NDArray


def append_samples_to_dataset(dataset_file_path: str, samples: NDArray[numpy.float64], labels: NDArray[numpy.float64]) -> None:
    """Appends the specified samples to the dataset.

    Args:
        dataset_file_path (str): The path to the dataset file, to which the samples are to be appended. If the dataset file does not exist, yet, it is
            created.
        samples (NDArray[numpy.float64]): The samples that are to be appended to the dataset.
        labels (NDArray[numpy.float64]): The labels of the samples that are to be appended to the dataset.
    """

    # If the dataset file does not exist, yet, it is created (the HDF5 datasets for the sample data and their ground-truth labels are created, but
    # they are made resizable, so that each time samples are appended, the HDF5 datasets can be resized to accommodate the new samples)
    if not os.path.exists(dataset_file_path):
        dataset_sample_shape = tuple(samples.shape[1:])
        with h5py.File(dataset_file_path, 'w') as dataset_file:
            dataset_file.create_dataset(
                'data',
                shape=(0,) + dataset_sample_shape,
                dtype='float32',
                maxshape=(None,) + dataset_sample_shape,
                chunks=True,
                compression='gzip'
            )
            dataset_file.create_dataset(
                'label',
                shape=(0,),
                dtype='uint16',
                maxshape=(None,),
                chunks=True,
                compression='gzip'
            )

    # Appends the dataset samples and their ground-truth labels to the dataset file
    with h5py.File(dataset_file_path, 'a') as dataset_file:

        # Determines how many samples are currently in the dataset and how many samples are being added (this is needed to correctly resize the HDF5
        # datasets)
        number_of_existing_samples = dataset_file['data'].shape[0]  # pylint: disable=no-member
        number_of_new_samples = samples.shape[0]

        # Resizes the HDF5 datasets for the sample data and their ground-truth labels, so that they can fit the samples that are to be appended
        dataset_file['data'].resize(number_of_existing_samples + number_of_new_samples, axis=0)  # pylint: disable=no-member
        dataset_file['label'].resize(number_of_existing_samples + number_of_new_samples, axis=0)  # pylint: disable=no-member

        # Appends the sample data and their ground-truth labels to the dataset
        dataset_file['data'][number_of_existing_samples:] = samples
        dataset_file['label'][number_of_existing_samples:] = labels


def append_attributions_to_attribution_database(
    attributions_file_path: str,
    attributions: NDArray[numpy.float64],
    predictions: NDArray[numpy.float64],
    labels: NDArray[numpy.int64]
) -> None:
    """Appends the specified attributions to the attributions database.

    Args:
        attributions_file_path (str): The path to the attributions database file, to which the attributions are to be appended. If the attributions
            database file does not exist, yet, it is created.
        attributions (NDArray[numpy.float64]): The attributions that are to be appended to the attributions database.
        predictions (NDArray[numpy.float64]): The predictions of the classifier for which the attributions were computed. that are to be appended to
            the attributions database.
        labels (NDArray[numpy.int64]): The ground-truth labels of the samples from which the attributions were computed, that are to be appended to
            the attributions database.
    """

    # If the attributions file does not exist, yet, it is created (the HDF5 datasets for the attributions, their predictions, and their ground-truth
    # labels are created, but they are made resizable, so that each time attributions are appended, the HDF5 datasets can be resized to accommodate
    # the new attributions)
    if not os.path.exists(attributions_file_path):
        attribution_shape = tuple(attributions.shape[1:])
        number_of_predictions = tuple(predictions.shape[1:])
        with h5py.File(attributions_file_path, 'w') as attributions_file:
            attributions_file.create_dataset(
                'attribution',
                shape=(0,) + attribution_shape,
                dtype='float32',
                maxshape=(None,) + attribution_shape,
                chunks=True,
                compression='gzip'
            )
            attributions_file.create_dataset(
                'prediction',
                shape=(0,) + number_of_predictions,
                dtype='float32',
                maxshape=(None,) + number_of_predictions,
                chunks=True,
                compression='gzip'
            )
            attributions_file.create_dataset(
                'label',
                shape=(0,),
                dtype='uint16',
                maxshape=(None,),
                chunks=True,
                compression='gzip'
            )

    # Appends the attributions, their predictions, and their ground-truth labels to the attributions file
    with h5py.File(attributions_file_path, 'a') as attributions_file:

        # Determines how many attributions are currently in the dataset and how many attributions are being added (this is needed to correctly resize
        # the HDF5 datasets)
        number_of_existing_attributions = attributions_file['attribution'].shape[0]  # pylint: disable=no-member
        number_of_new_attributions = attributions.shape[0]

        # Resizes the HDF5 datasets for the attributions, their predictions, and their ground-truth labels, so that they can fit the attributions that
        # are to be appended
        attributions_file['attribution'].resize(number_of_existing_attributions + number_of_new_attributions, axis=0)  # pylint: disable=no-member
        attributions_file['prediction'].resize(number_of_existing_attributions + number_of_new_attributions, axis=0)  # pylint: disable=no-member
        attributions_file['label'].resize(number_of_existing_attributions + number_of_new_attributions, axis=0)  # pylint: disable=no-member

        # Appends the attributions, their predictions, and their ground-truth labels to the attributions file
        attributions_file['attribution'][number_of_existing_attributions:] = attributions
        attributions_file['prediction'][number_of_existing_attributions:] = predictions
        attributions_file['label'][number_of_existing_attributions:] = labels


def make_test_data(
    dataset_file_path: str,
    attribution_file_path: str,
    label_map_file_path: str,
    number_of_classes: int,
    number_of_samples: int,
    append: bool
) -> None:
    """Randomly generates a dataset and attributions for the samples in the dataset and writes them to an HDF5 dataset
    file and an HDF5 attribution database file.

    Args:
        dataset_file_path (str): The path to the dataset file that is to be created or appended to.
        attribution_file_path (str): The path to the attributions database file that is to be created or appended to.
        label_map_file_path (str): The path to the label map file that is to be created.
        number_of_classes (int): The number of classes for which samples are to be generated randomly.
        number_of_samples (int): The number of dataset samples that are to be generated randomly (directly corresponds to the number of attributions
            that are to be generated randomly, because a single attribution is generated for each sample).
        append (bool): Determines whether the new dataset samples and attributions are to be appended to existing dataset and attribution database
            files or whether existing files are to be overwritten. If no dataset or attribution database files exist, they are generated either way.
    """

    # Creates the label map file
    label_map = [{
        'index': index,
        'word_net_id': f'{index:08d}',
        'name': f'Class {index:d}',
    } for index in range(number_of_classes)]
    with open(label_map_file_path, 'w', encoding='utf-8') as label_map_file:
        json.dump(label_map, label_map_file)

    # If a previous dataset and attribution database is to be overwritten, then they are deleted so that they can be re-created instead of appending
    # to them
    if not append:
        for file_path in (dataset_file_path, attribution_file_path):
            if os.path.exists(file_path):
                os.remove(file_path)

    # Cycles through all labels that are to be generated
    for label_index in range(number_of_classes):

        # Creates the dataset samples, their labels, their attributions, and the classifier predictions randomly
        samples = numpy.random.uniform(0, 1, size=(number_of_samples, 3, 32, 32))
        labels = numpy.array([label_index] * number_of_samples)
        attributions = numpy.random.uniform(-1, 1, size=(number_of_samples, 3, 32, 32))
        predictions = numpy.random.uniform(0, 1, size=(number_of_samples, number_of_classes))

        # Appends the new dataset samples and attributions to the dataset and attribution database files (if the dataset file or the attribution
        # database file already exist, they are created on the fly)
        append_samples_to_dataset(dataset_file_path, samples, labels)
        append_attributions_to_attribution_database(attribution_file_path, attributions, predictions, labels)


def main() -> None:
    """The entrypoint to the make_test_data script."""

    argument_parser = argparse.ArgumentParser(
        prog='make_test_data',
        description='''Generates a random dataset and random attributions for this dataset, which can then be used to generate a meta-analysis and
            ultimately a test project for ViRelAy.'''
    )
    argument_parser.add_argument(
        'dataset_file_path',
        type=str,
        help='The path to the dataset file that is to be created or appended to.'
    )
    argument_parser.add_argument(
        'attribution_file_path',
        type=str,
        help='The path to the attributions database file that is to be created or appended to.'
    )
    argument_parser.add_argument(
        'label_map_file_path',
        type=str,
        help='The path to the label map file that is to be created.'
    )
    argument_parser.add_argument(
        '-c',
        '--number-of-classes',
        dest='number_of_classes',
        type=int,
        default=10,
        help='The number of classes for which samples are to be generated randomly. Defaults to 10.'
    )
    argument_parser.add_argument(
        '-s',
        '--number-of-samples',
        dest='number_of_samples',
        type=int,
        default=100,
        help='''The number of dataset samples that are to be generated randomly (directly corresponds to the number of attributions that are to be
            generated randomly, because a single attribution is generated for each sample). Defaults to 100.'''
    )
    argument_parser.add_argument(
        '-a',
        '--append',
        dest='append',
        action='store_true',
        help='''Determines whether the new dataset samples and attributions are to be appended to existing dataset and attribution database files or
            whether existing files are to be overwritten. If no dataset or attribution database files exist, they are generated either way.'''
    )
    arguments = argument_parser.parse_args()

    make_test_data(
        arguments.dataset_file_path,
        arguments.attribution_file_path,
        arguments.label_map_file_path,
        arguments.number_of_classes,
        arguments.number_of_samples,
        arguments.append
    )


if __name__ == '__main__':
    main()
