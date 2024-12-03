"""Converts the CIFAR-10 dataset into the correct HDF5 format that is required by ViRelAy."""

import json
import argparse

import h5py
import torch
import numpy
from torchvision.datasets import CIFAR10


def create_dataset(dataset_file_path: str, samples_shape: tuple[int, ...], number_of_samples: int) -> h5py.File:
    """Creates a new dataset HDF5 file.

    Args:
        dataset_file_path (str): The path to the dataset HDF5 file that is to be created.
        samples_shape (tuple[int, ...]): The shape of the samples in the dataset.
        number_of_samples (int): The number of samples in the dataset.

    Returns:
        h5py.File: Returns the file handle to the attributions database.
    """

    dataset_file = h5py.File(dataset_file_path, 'w')
    dataset_file.create_dataset('data', shape=(number_of_samples,) + samples_shape, dtype=numpy.float32)
    dataset_file.create_dataset('label', shape=(number_of_samples,), dtype=numpy.uint16)
    return dataset_file


def append_sample(
    dataset_file: h5py.File,
    index: int,
    sample: torch.Tensor,
    label: torch.Tensor
) -> None:
    """Appends the specified sample to the dataset.

    Args:
        dataset_file (h5py.File): The file handle to the dataset to which the sample is to be appended.
        index (int): The index of the sample.
        sample (torch.Tensor): The sample that is to be appended.
        label (torch.Tensor): The ground-truth label of the sample.
    """

    dataset_file['data'][index] = sample
    dataset_file['label'][index] = label


def make_dataset(dataset_path: str, output_file_path: str, label_map_file_path: str) -> None:
    """Converts the CIFAR-10 dataset into the HDF5 format, which can be consumed by ViRelAy.

    Args:
        dataset_path (str): The path to the CIFAR-10 dataset. If it does not exist, it is automatically downloaded.
        output_file_path (str): The path to the HDF5 file into which the dataset is to be stored.
        label_map_file_path (str): The path to the file into which the label map is to be stored.
    """

    train_dataset = CIFAR10(root=dataset_path, train=True, download=True)
    number_of_samples = len(train_dataset)
    number_of_classes = 10
    sample_shape = (3, 32, 32)

    classes = ['Airplane', 'Automobile', 'Bird', 'Cat', 'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']
    wordnet_ids = [
        'n02691156',
        'n02958343',
        'n01503061',
        'n02121620',
        'n02430045',
        'n02084071',
        'n01639765',
        'n02374451',
        'n04194289',
        'n04490091'
    ]
    label_map = [{
        'index': index,
        'word_net_id': wordnet_ids[index],
        'name': classes[index],
    } for index in range(number_of_classes)]
    with open(label_map_file_path, 'w', encoding='utf-8') as label_map_file:
        json.dump(label_map, label_map_file)

    with create_dataset(output_file_path, sample_shape, number_of_samples) as dataset_file:
        for index, (sample, label) in enumerate(train_dataset):
            sample = numpy.array(sample)
            sample = numpy.transpose(sample, (2, 0, 1))
            append_sample(dataset_file, index, sample, label)
            if (index + 1) % 10 == 0:
                print(f'Converted {index + 1}/{number_of_samples} samples')


def main() -> None:
    """The entrypoint to the make_dataset script."""

    argument_parser = argparse.ArgumentParser(
        prog='train_vgg',
        description='Trains a VGG16 model on CIFAR-10.'
    )
    argument_parser.add_argument(
        'dataset_path',
        type=str,
        help='The path to the CIFAR-10 dataset. If it does not exist, it is automatically downloaded.'
    )
    argument_parser.add_argument(
        'output_file_path',
        type=str,
        help='The path to the HDF5 file into which the dataset is to be stored.'
    )
    argument_parser.add_argument(
        'label_map_file_path',
        type=str,
        help='The path to the file into which the label map is to be stored.'
    )
    arguments = argument_parser.parse_args()

    make_dataset(arguments.dataset_path, arguments.output_file_path, arguments.label_map_file_path)


if __name__ == '__main__':
    main()
