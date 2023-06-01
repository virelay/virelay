import h5py
from torch import Tensor
from torchvision.datasets import ImageFolder
import os
import torch.nn as nn
from corelay.base import Param
from corelay.processor.base import Processor
from corelay.processor.distance import SciPyPDist
from corelay.processor.flow import Sequential
import numpy as np


class AllowEmptyClassImageFolder(ImageFolder):
    '''Subclass of ImageFolder, which only finds non-empty classes, but with their correct indices given other empty
    classes. This counter-acts the changes in torchvision 0.10.0, in which DatasetFolder does not allow empty classes
    anymore by default. Versions before 0.10.0 do not expose `find_classes`, and thus this change does not change the
    functionality of `ImageFolder` in earlier versions.
    '''

    def find_classes(self, directory):
        with os.scandir(directory) as scanit:
            class_info = sorted((entry.name, len(list(os.scandir(entry.path)))) for entry in scanit if entry.is_dir())
        class_to_idx = {class_name: index for index, (class_name, n_members) in enumerate(class_info) if n_members}
        if not class_to_idx:
            raise FileNotFoundError(f'No non-empty classes found in \'{directory}\'.')
        return list(class_to_idx), class_to_idx


def create_attribution_database(
        attribution_database_file_path: str,
        attribution_shape: tuple,  # pylint: disable=no-member
        number_of_classes: int,
        number_of_samples: int) -> None:
    """Creates a new attribution database HDF5 file.

    Parameters
    ----------
        attribution_database_file_path: str
            The path to the attribution database HDF5 file that is to be created.
        attribution_shape: torch.Size
            The shape of the attributions.
        number_of_samples: int
            The number of samples in the dataset.

    Returns
    -------
        h5py.File
            Returns the file handle to the attributions database.
    """

    attribution_database_file = h5py.File(attribution_database_file_path, 'w')
    attribution_database_file.create_dataset(
        'attribution',
        shape=(number_of_samples,) + attribution_shape,
        dtype='float32'
    )
    attribution_database_file.create_dataset(
        'prediction',
        shape=(number_of_samples, number_of_classes),
        dtype='float32'
    )
    attribution_database_file.create_dataset(
        'label',
        shape=(number_of_samples,),
        dtype='uint16'
    )
    return attribution_database_file


def append_attributions(
        attribution_database_file: h5py.File,
        index: int,
        attributions: Tensor,
        predictions: Tensor,
        labels: Tensor) -> None:
    """Appends the specified attributions to the attribution database.

    Args:
        attribution_database_file: str
            The file handle to the attributions database to which the attribution is to be appended.
        index: int
            The index where the attributions are to be inserted.
        attributions: torch.Tensor
            The attribution that is to be appended.
        predictions: torch.Tensor
            The prediction of the classifier.
        labels: torch.Tensor
            The ground-truth label of the sample for which the attribution was computed.
    """

    attribution_database_file['attribution'][index:attributions.shape[0] + index] = attributions.cpu().detach().numpy()
    attribution_database_file['prediction'][index:predictions.shape[0] + index] = predictions.detach().cpu().numpy()
    attribution_database_file['label'][index:labels.shape[0] + index] = labels.cpu().detach().numpy()


class Flatten(Processor):
    """Represents a CoRelAy processor, which flattens its input data."""

    def function(self, data:np.ndarray) ->np.ndarray:
        """Applies the flattening to the input data.

        Parameters
        ----------
            data:np.ndarray
                The input data that is to be flattened.

        Returns
        -------
           np.ndarray
                Returns the flattened data.
        """

        return data.reshape(data.shape[0],np.prod(data.shape[1:]))


class SumChannel(Processor):
    """Represents a CoRelAy processor, which sums its input data across channels, i.e., its second axis."""

    def function(self, data:np.ndarray) ->np.ndarray:
        """Applies the summation over the channels to the input data.

        Parameters
        ----------
            data:np.ndarray
                The input data that is to be summed over its channels.

        Returns
        -------
           np.ndarray
                Returns the data that was summed up over its channels.
        """

        return data.sum(axis=1)


class Absolute(Processor):
    """Represents a CoRelAy processor, which computes the absolute value of its input data."""

    def function(self, data:np.ndarray) ->np.ndarray:
        """Computes the absolute value of the specified input data.

        Parameters
        ----------
            data:np.ndarray
                The input data for which the absolute value is to be computed.

        Returns
        -------
           np.ndarray
                Returns the absolute value of the input data.
        """

        return np.absolute(data)


class Normalize(Processor):
    """Represents a CoRelAy processor, which normalizes its input data.

    Attributes
    ----------
        axes: Param
            A parameter of the processor, which determines the axis over which the data is to be normalized. Defaults to
            the second and third axes.
    """

    axes = Param(tuple, (1, 2))

    def function(self, data:np.ndarray) -> np.ndarray:
        """Normalizes the specified input data.

        Parameters
        ----------
            data:np.ndarray
                The input data that is to be normalized.

        Returns
        -------
           np.ndarray
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

    def function(self, data:np.ndarray) ->np.ndarray:
        """Computes histograms over the specified input data. One histogram is computed for each channel and each sample
        in a batch of input data.

        Parameters
        ----------
            data: np.ndarray
                The input data over which the histograms are to be computed.

        Returns
        -------
            np.ndarray
                Returns the histograms that were computed over the input data.
        """

        return np.stack([
           np.stack([
               np.histogram(
                    sample.reshape(sample.shape[0],np.prod(sample.shape[1:3])),
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