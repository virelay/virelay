"""Uses LRP to generate attributions for a VGG16 model trained on CIFAR-10."""

import argparse

import h5py
import numpy
import torch
from torchvision import transforms
from torchvision.models import vgg16
from torchvision.datasets import CIFAR10

from zennit.attribution import Gradient
from zennit.composites import EpsilonGammaBox


def create_attribution_database(
    attribution_database_file_path: str,
    attribution_shape: torch.Size,
    number_of_classes: int,
    number_of_samples: int
) -> h5py.File:
    """Creates a new attribution database HDF5 file.

    Args:
        attribution_database_file_path (str): The path to the attribution database HDF5 file that is to be created.
        attribution_shape (torch.Size): The shape of the attributions.
        number_of_classes (int): The number of classes in the dataset.
        number_of_samples (int): The number of samples in the dataset.

    Returns:
        h5py.File: Returns the file handle to the attributions database.
    """

    attribution_database_file = h5py.File(attribution_database_file_path, 'w')
    attribution_database_file.create_dataset('attribution', shape=(number_of_samples,) + tuple(attribution_shape), dtype=numpy.float32)
    attribution_database_file.create_dataset('prediction', shape=(number_of_samples, number_of_classes), dtype=numpy.float32)
    attribution_database_file.create_dataset('label', shape=(number_of_samples,), dtype=numpy.uint16)
    return attribution_database_file


def append_attributions(
    attribution_database_file: h5py.File,
    index: int,
    attributions: torch.Tensor,
    predictions: torch.Tensor,
    labels: torch.Tensor
) -> None:
    """Appends the specified attributions to the attribution database.

    Args:
        attribution_database_file (h5py.File): The file handle to the attributions database to which the attribution is to be appended.
        index (int): The index where the attributions are to be inserted.
        attributions (torch.Tensor): The attribution that is to be appended.
        predictions (torch.Tensor): The prediction of the classifier.
        labels (torch.Tensor): The ground-truth label of the sample for which the attribution was computed.
    """

    attribution_database_file['attribution'][index:attributions.shape[0] + index] = attributions.detach().numpy()
    attribution_database_file['prediction'][index:predictions.shape[0] + index] = predictions.detach().numpy()
    attribution_database_file['label'][index:labels.shape[0] + index] = labels.detach().numpy()


def explain_vgg(dataset_path: str, model_file_path: str, attribution_database_file_path: str, batch_size: int) -> None:
    """Uses LRP to generate attributions for a trained VGG16 model.

    Args:
        dataset_path (str): The path to the CIFAR-10 dataset. If it does not exist, it is automatically downloaded.
        model_file_path (str): The path to the file that contains the weights of the trained VGG16 model.
        attribution_database_file_path (str): The path to the attribution database HDF5 file that is to be created.
        batch_size (int): The batch size that is to be used during the computation of the attributions.
    """

    model = vgg16(num_classes=10)
    state_dict = torch.load(model_file_path, map_location='cpu')
    model.load_state_dict(state_dict)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    train_dataset = CIFAR10(root=dataset_path, train=True, download=True, transform=transform)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
    number_of_samples = len(train_dataset)
    number_of_classes = 10

    with create_attribution_database(
        attribution_database_file_path,
        train_dataset[0][0].shape,
        number_of_classes,
        number_of_samples
    ) as attribution_database_file:

        composite = EpsilonGammaBox(low=-3.0, high=3.0)
        attributor = Gradient(model=model, composite=composite)

        number_of_samples_processed = 0
        with attributor:
            for batch, labels in train_loader:
                predictions, attributions = attributor(batch, torch.eye(number_of_classes)[labels])

                append_attributions(attribution_database_file, number_of_samples_processed, attributions, predictions, labels)
                number_of_samples_processed += attributions.shape[0]

                print(f'Computed {number_of_samples_processed}/{number_of_samples} attributions')


def main() -> None:
    """The entrypoint to the explain_vgg script."""

    argument_parser = argparse.ArgumentParser(
        prog='train_vgg',
        description='Generates attributions for a VGG16 model trained on CIFAR-10 using LRP.'
    )
    argument_parser.add_argument(
        'dataset_path',
        type=str,
        help='The path to the CIFAR-10 dataset. If it does not exist, it is automatically downloaded.'
    )
    argument_parser.add_argument(
        'model_file_path',
        type=str,
        help='The path to the file that contains the weights of the trained VGG16 model.'
    )
    argument_parser.add_argument(
        'attribution_database_file_path',
        type=str,
        help='The path to the file into which the generated attribution database is to be written.'
    )
    argument_parser.add_argument(
        '-b',
        '--batch-size',
        dest='batch_size',
        type=int,
        default=64,
        help='The batch size that is to be used during the computation of the attributions. Defaults to 64.'
    )
    arguments = argument_parser.parse_args()

    explain_vgg(
        arguments.dataset_path,
        arguments.model_file_path,
        arguments.attribution_database_file_path,
        arguments.batch_size
    )


if __name__ == '__main__':
    main()
