"""Contains the data model abstraction."""
# pylint: disable=too-many-lines

import os
import re
import json
import glob

import yaml
import h5py
import numpy
import matplotlib.cm
from PIL import Image


class Project:
    """Represents a single project, which can be loaded from a YAML file."""

    def __init__(self, path):
        """
        Initializes a new Project instance.

        Parameters
        ----------
            path: str
                The path to the YAML file that contains the project definition.

        Raises
        ------
            ValueError
                If the project file is incorrect or corrupted, a ValueError is raised.
                If the specified dataset type is unknown, then a ValueError is raised.
        """

        # Initializes some class members
        self.is_closed = False
        self.dataset = None
        self.attributions = []
        self.analyses = []

        # Stores the path for later reference
        self.path = path

        # Loads the project from the YAML file
        working_directory = os.path.dirname(self.path)
        with open(self.path, 'r') as project_file:
            try:

                # Loads the project and extracts some general information
                project = yaml.safe_load(project_file)['project']
                self.name = project['name']
                self.model = project['model']

                # Loads the label map, which is used to get the human-readable names of the labels referenced in the
                # dataset as well as in the attributions and analyses databases
                self.label_map = LabelMap(os.path.join(working_directory, project['label_map']))

                # Loads the dataset of the project
                if project['dataset'] is not None:
                    dataset_type = project['dataset']['type']
                    if dataset_type == 'hdf5':
                        self.dataset = Hdf5Dataset(
                            project['dataset']['name'],
                            os.path.join(working_directory, project['dataset']['path']),
                            self.label_map
                        )
                    elif dataset_type == 'image_directory':
                        self.dataset = ImageDirectoryDataset(
                            project['dataset']['name'],
                            os.path.join(working_directory, project['dataset']['path']),
                            project['dataset']['label_index_regex'],
                            project['dataset']['label_word_net_id_regex'],
                            self.label_map
                        )
                    else:
                        raise ValueError('The specified dataset type "{0}" is unknown.'.format(dataset_type))

                # Loads the attributions of the project
                if project['attributions'] is not None:
                    for attribution in project['attributions']:
                        self.attributions.append(AttributionDatabase(
                            os.path.join(working_directory, attribution['attribution']),
                            attribution['attribution_method'],
                            attribution['attribution_strategy'],
                            self.label_map
                        ))

                # Loads the analyses of the project
                if project['analyses'] is not None:
                    for analysis in project['analyses']:
                        self.analyses.append(AnalysisDatabase(
                            os.path.join(working_directory, analysis['analysis']),
                            analysis['analysis_method'],
                            self.label_map
                        ))
            except yaml.YAMLError:
                raise ValueError('An error occurred while loading the project file.')

    def close(self):
        """Closes the project, its dataset, and all of its sources."""

        if not self.is_closed:
            if self.dataset is not None:
                self.dataset.close()
            for attribution in self.attributions:
                attribution.close()
            for analysis in self.analyses:
                analysis.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the project."""

        self.close()


class AttributionDatabase:
    """Represents a single attribution database, which contains the attributions for the dataset samples."""

    def __init__(self, attribution_path, attribution_method, attribution_strategy, label_map):
        """
        Initializes a new AttributionDatabase instance.

        Parameters
        ----------
            attribution_path: str
                The path to the file that contains the attribution database.
            attribution_method: str
                The name of the method that was used to calculate the attribution. Currently 'lrp_composite' for LRP
                Composite and 'lrp_composite_flat' for LRP Composite + flat are supported.
            attribution_strategy: str
                The strategy that was employed for the attribution. This can either be 'true_label' (the attribution was
                performed for the ground truth), 'predicted_label' (the attribution was performed for the label that was
                predicted by the model), or a class index (this is the class index of the class for which the
                attribution was performed.
            label_map: LabelMap
                The label map, which contains a mapping between the index of the labels and their human-readable names.

        Raises
        ------
            ValueError
                If the specified attribution method is unknown, a ValueError is raised.
                If the specified attribution strategy is unknown, a ValueError is raised.
        """

        # Initializes some class members
        self.is_closed = False
        self.attribution_file = None

        # Validates the arguments
        if attribution_method not in ['lrp_composite', 'lrp_composite_flat']:
            raise ValueError('The specified attribution method {0} is unknown'.format(attribution_method))
        if attribution_strategy not in ['true_label', 'predicted_label'] and not isinstance(attribution_strategy, int):
            raise ValueError('The specified attribution strategy {0} is unknown.'.format(attribution_strategy))

        # Stores the arguments for later reference
        self.attribution_path = attribution_path
        self.attribution_method = attribution_method
        self.attribution_strategy = attribution_strategy
        self.label_map = label_map

        # Loads the attribution files
        self.attribution_file = h5py.File(self.attribution_path)

        # Determines if the dataset allows multiple labels or only single labels (when the dataset is multi-label, then
        # the labels are stored as a boolean NumPy array where the index is the label index and the value determines
        # whether the sample has the label, when the dataset is single-label, then the label is just a scalar value
        # containing the index of the label)
        self.is_multi_label = self.attribution_file['label'][0].dtype == numpy.bool

    def has_attribution(self, index):
        """
        Determines whether the attribution database contains the attribution with the specified index.

        Parameters
        ----------
            index: int
                The index that is to be checked.

        Raises
        ------
            ValueError
                If the attribution database has already been closed, then a ValueError is raised.

        Returns
        -------
            bool
                Returns True if the database contains the attribution with the specified index and False otherwise.
        """

        if self.is_closed:
            raise ValueError('The analysis database has already been closed.')

        return index in self.attribution_file['index']

    def get_attribution(self, index):
        """
        Gets the attribution with the specified index.

        Parameters
        ----------
            index: int
                The index of the attribution that is to be retrieved.

        Raises
        ------
            ValueError
                If the attribution database has already been closed, then a ValueError is raised.
            IndexError
                When the no attribution with the specified index exists, then an IndexError is raised.

        Returns
        -------
            Attribution
                Returns the attribution with the specified index.
        """

        # Checks if the attribution database has already been closed, if so, a ValueError is raised
        if self.is_closed:
            raise ValueError('The analysis database has already been closed.')

        # Checks if the specified attribution exists, if not, then an IndexError is raised
        if not self.has_attribution(index):
            raise IndexError()

        # Extracts the information about the sample from the dataset
        attribution_data = self.attribution_file['attribution'][index]
        attribution_label_reference = self.attribution_file['label'][index]
        if self.is_multi_label:
            attribution_labels = self.label_map.get_labels_from_n_hot_vector(attribution_label_reference)
        else:
            attribution_labels = [self.label_map.get_label_from_index(attribution_label_reference)]
        attribution_prediction = self.attribution_file['prediction'][index]

        # Wraps the attribution in an object and returns it
        return Attribution(
            index,
            attribution_data,
            attribution_labels,
            attribution_prediction,
            self.attribution_method,
            self.attribution_strategy
        )

    def close(self):
        """Closes the attribution database."""

        if not self.is_closed:
            if self.attribution_file is not None:
                self.attribution_file.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the attribution database."""

        self.close()


class Attribution:
    """Represents a single attribution from an attribution database."""

    def __init__(self, index, data, labels, prediction, attribution_method, attribution_strategy):
        """
        Initializes a new Attribution instance.

        Parameters
        ----------
            index: int
                The index of the attribution, which is the index of the sample for which the attribution was created.
            data: numpy.ndarray
                The attribution data, which is a raw heatmap.
            labels: list
                A list of the ground truth labels of the sample for which the attribution was created.
            prediction: numpy.ndarray
                The original output of the model.
            attribution_method: str
                The name of the method that was used to calculate the attribution. Currently 'lrp_composite' for LRP
                Composite and 'lrp_composite_flat' for LRP Composite + flat are supported.
            attribution_strategy: str
                The strategy that was employed for the attribution. This can either be 'true_label' (the attribution was
                performed for the ground truth), 'predicted_label' (the attribution was performed for the label that was
                predicted by the model), or a class index (this is the class index of the class for which the
                attribution was performed.
        """

        # Stores the parameters for later use
        self.index = index
        self.data = data
        self.labels = labels
        self.prediction = prediction
        self.attribution_method = attribution_method
        self.attribution_strategy = attribution_strategy

        # Heatmaps (the attribution data) may come from different sources, e.g. in PyTorch the ordering of the axes is
        # Channels x Width x Height, while in other sources, the ordering is Width x Height x Channel, this code tries
        # to guess which axis represents the RGB channels, and puts them in the order Width x Height x Channel
        if numpy.argmin(self.data.shape) == 0:
            self.data = numpy.moveaxis(self.data, [0, 1, 2], [2, 0, 1])

    def render_heatmap(self, color_map):
        """
        Takes the raw attribution data and converts it so that the data can be visualized as a heatmap.

        Parameters
        ----------
            color_map: str
                The name of color map that is to be used to render the heatmap.

        Raises
        ------
            ValueError
                If the specified color map is unknown, then a ValueError is raised.
        """

        # Creates a dictionary, which maps the name of a custom color map to a method that produces the heatmap image
        # using that color map
        custom_color_maps = {
            'gray-red-1': Attribution.generate_heatmap_image_gray_red_1,
            'gray-red-2': Attribution.generate_heatmap_image_gray_red_2,
            'black-green': Attribution.generate_heatmap_image_black_green,
            'black-fire-red': Attribution.generate_heatmap_image_black_fire_red,
            'blue-black-yellow': Attribution.generate_heatmap_image_black_yellow
        }

        # Creates a list of 'fall-back'-color-maps from matplotlib, which can also be used
        matplotlib_color_maps = {
            'blue-white-red': 'bwr',
            'afmhot': 'afmhot',
            'jet': 'jet',
            'seismic': 'seismic'
        }

        # Checks if the raw attribution has more than one channel, in that case the channels are summed up
        if len(self.data.shape) == 3 and self.data.shape[-1] > 1:
            data = numpy.sum(self.data, axis=2)
        else:
            data = self.data

        # Checks the name of the color map and renders the heatmap image accordingly, if the color map is not supported,
        # then an exception is raised
        if color_map in custom_color_maps:
            return custom_color_maps[color_map](data)
        elif color_map in matplotlib_color_maps:
            return Attribution.generate_heatmap_image_using_matplotlib(data, matplotlib_color_maps[color_map])
        else:
            raise ValueError('The color map "{0}" is not supported.'.format(color_map))

    @staticmethod
    def generate_heatmap_image_using_matplotlib(raw_heatmap, color_map_name):
        """
        Generates a heatmap image from the specified raw heatmap using the color maps provided by matplotlib.

        Parameters
        ----------
            raw_heatmap: numpy.ndarray
                The raw heatmap, which are to be converted into an image representation.
            color_map_name: str
                The name of the color map that is used to produce the image heatmap.

        Returns
        -------
            numpy.ndarray
                Returns an array that contains the RGB values of the resulting heatmap image.
        """

        # Gets the color map specified by the name
        color_map = getattr(matplotlib.cm, color_map_name)

        # Brings the raw heatmap data into a value range of 0.0 and 1.0
        raw_heatmap = raw_heatmap / numpy.max(numpy.abs(raw_heatmap))
        raw_heatmap = (raw_heatmap + 1.0) / 2.0

        # Applies the color map to the raw heatmap
        heatmap_height, heatmap_width = raw_heatmap.shape
        heatmap_image = color_map(raw_heatmap.flatten())
        heatmap_image = heatmap_image[:, 0:3].reshape([heatmap_height, heatmap_width, 3])

        # Returns the created heatmap image
        return heatmap_image

    @staticmethod
    def generate_heatmap_image_gray_red_1(raw_heatmap):
        """
        Generates a heatmap with a gray background, where red tones are used to visualize positive relevance values and
        blue tones are used to visualize negative relevances.

        Parameters
        ----------
            raw_heatmap: numpy.ndarray
                The raw heatmap, which are to be converted into an image representation.

        Returns
        -------
            numpy.ndarray
                Returns an array that contains the RGB values of the resulting heatmap image.
        """

        # Creates the floating point representation of a the base gray color that is used in the heatmap, and creates a
        # new heatmap image, with that base gray as the background color
        basegray = 0.8
        heatmap_image = numpy.ones([raw_heatmap.shape[0], raw_heatmap.shape[1], 3]) * basegray

        # Generates the actual heatmap image
        absolute_maximum = numpy.max(raw_heatmap)
        truncated_values = numpy.maximum(numpy.minimum(raw_heatmap / absolute_maximum, 1.0), -1.0)
        negatives = raw_heatmap < 0
        heatmap_image[negatives, 0] += truncated_values[negatives] * basegray
        heatmap_image[negatives, 1] += truncated_values[negatives] * basegray
        heatmap_image[negatives, 2] += -truncated_values[negatives] * (1 - basegray)
        positives = raw_heatmap >= 0
        heatmap_image[positives, 0] += truncated_values[positives] * (1 - basegray)
        heatmap_image[positives, 1] += -truncated_values[positives] * basegray
        heatmap_image[positives, 2] += -truncated_values[positives] * basegray

        # Returns the created heatmap image
        return heatmap_image

    @staticmethod
    def generate_heatmap_image_gray_red_2(raw_heatmap):
        """
        Generates a heatmap with a gray background, where red tones are used to visualize positive relevance values and
        blue tones are used to visualize negative relevances.

        Parameters
        ----------
            raw_heatmap: numpy.ndarray
                The raw heatmap, which are to be converted into an image representation.

        Returns
        -------
            numpy.ndarray
                Returns an array that contains the RGB values of the resulting heatmap image.
        """

        # Prepares the raw heatmap
        variance = numpy.var(raw_heatmap)
        raw_heatmap[raw_heatmap > 10 * variance] = 0
        raw_heatmap[raw_heatmap < 0] = 0
        raw_heatmap = raw_heatmap / numpy.max(raw_heatmap)

        # Applies the heatmap to the positive relevances
        heatmap_red_positive = 0.9 - numpy.clip(raw_heatmap - 0.3, 0, 0.7) / 0.7 * 0.5
        heatmap_green_positive = \
            0.9 - numpy.clip(raw_heatmap - 0.0, 0, 0.3) / 0.3 * \
            0.5 - numpy.clip(raw_heatmap - 0.3, 0, 0.7) / 0.7 * 0.4
        heatmap_blue_positive = \
            0.9 - numpy.clip(raw_heatmap - 0.0, 0, 0.3) / 0.3 * \
            0.5 - numpy.clip(raw_heatmap - 0.3, 0, 0.7) / 0.7 * 0.4

        # Applies the heatmap to the negative relevances
        heatmap_red_negative = \
            0.9 - numpy.clip(-raw_heatmap - 0.0, 0, 0.3) / 0.3 * \
            0.5 - numpy.clip(-raw_heatmap - 0.3, 0, 0.7) / 0.7 * 0.4
        heatmap_green_negative = \
            0.9 - numpy.clip(-raw_heatmap - 0.0, 0, 0.3) / 0.3 * \
            0.5 - numpy.clip(-raw_heatmap - 0.3, 0, 0.7) / 0.7 * 0.4
        heatmap_blue_negative = 0.9 - numpy.clip(-raw_heatmap - 0.3, 0, 0.7) / 0.7 * 0.5

        # Combines the positive and negative relevances
        heatmap_red = heatmap_red_positive * (raw_heatmap >= 0) + heatmap_red_negative * (raw_heatmap < 0)
        heatmap_green = heatmap_green_positive * (raw_heatmap >= 0) + heatmap_green_negative * (raw_heatmap < 0)
        heatmap_blue = heatmap_blue_positive * (raw_heatmap >= 0) + heatmap_blue_negative * (raw_heatmap < 0)

        # Concatenates the individual color channels back together and returns the generated heatmap image
        return numpy.concatenate([
            heatmap_red[..., None],
            heatmap_green[..., None],
            heatmap_blue[..., None]
        ], axis=2)

    @staticmethod
    def generate_heatmap_image_black_green(raw_heatmap):
        """
        Generates a heatmap with a black background, where green tones are used to visualize positive relevance values
        and blue tones are used to visualize negative relevances.

        Parameters
        ----------
            raw_heatmap: numpy.ndarray
                The raw heatmap, which are to be converted into an image representation.

        Returns
        -------
            numpy.ndarray
                Returns an array that contains the RGB values of the resulting heatmap image.
        """

        # Creates the heatmap image with all pixel values set to 0
        absolute_maximum = numpy.max(raw_heatmap)
        heatmap_image = numpy.zeros([raw_heatmap.shape[0], raw_heatmap.shape[1], 3])

        # Applies the heatmap to the negative relevances
        negatives = raw_heatmap < 0
        heatmap_image[negatives, 2] = -raw_heatmap[negatives] / absolute_maximum

        # Applies the heatmap to the positive relevances
        positives = raw_heatmap >= 0
        heatmap_image[positives, 1] = raw_heatmap[positives] / absolute_maximum

        # Returns the generated heatmap image
        return heatmap_image

    @staticmethod
    def generate_heatmap_image_black_fire_red(raw_heatmap):
        """
        Generates a heatmap with a gray background, where red tones are used to visualize positive relevance values and
        blue tones are used to visualize negative relevances.

        Parameters
        ----------
            raw_heatmap: numpy.ndarray
                The raw heatmap, which are to be converted into an image representation.

        Returns
        -------
            numpy.ndarray
                Returns an array that contains the RGB values of the resulting heatmap image.
        """

        # Prepares the raw heatmap
        raw_heatmap = raw_heatmap / numpy.max(numpy.abs(raw_heatmap))

        # Applies the heatmap to the positive relevances
        heatmap_red_positive = numpy.clip(raw_heatmap - 0.00, 0, 0.25) / 0.25
        heatmap_green_positive = numpy.clip(raw_heatmap - 0.25, 0, 0.25) / 0.25
        heatmap_blue_positive = numpy.clip(raw_heatmap - 0.50, 0, 0.50) / 0.50

        # Applies the heatmap to the negative relevances
        heatmap_red_negative = numpy.clip(-raw_heatmap - 0.50, 0, 0.50) / 0.50
        heatmap_green_negative = numpy.clip(-raw_heatmap - 0.25, 0, 0.25) / 0.25
        heatmap_blue_negative = numpy.clip(-raw_heatmap - 0.00, 0, 0.25) / 0.25

        # Combines the positive and negative relevances, concatenates the individual color channels back together, and
        # returns the generated heatmap image
        return numpy.concatenate([
            (heatmap_red_positive + heatmap_red_negative)[..., None],
            (heatmap_green_positive + heatmap_green_negative)[..., None],
            (heatmap_blue_positive + heatmap_blue_negative)[..., None]
        ], axis=2)

    @staticmethod
    def generate_heatmap_image_black_yellow(raw_heatmap):
        """
        Generates a heatmap with a black background, where yellow tones are used to visualize positive relevance values
        and blue tones are used to visualize negative relevances.

        Parameters
        ----------
            raw_heatmap: numpy.ndarray
                The raw heatmap, which are to be converted into an image representation.

        Returns
        -------
            numpy.ndarray
                Returns an array that contains the RGB values of the resulting heatmap image.
        """

        # Creates the heatmap image with all pixel values set to 0
        absolute_maximum = numpy.max(raw_heatmap)
        heatmap_image = numpy.zeros([raw_heatmap.shape[0], raw_heatmap.shape[1], 3])

        # Applies the heatmap to the negative relevances
        negatives = raw_heatmap < 0
        heatmap_image[negatives, 2] = -raw_heatmap[negatives] / absolute_maximum

        # Applies the heatmap to the positive relevances
        positives = raw_heatmap >= 0
        heatmap_image[positives, 0] = raw_heatmap[positives] / absolute_maximum
        heatmap_image[positives, 1] = raw_heatmap[positives] / absolute_maximum

        # Returns the generated heatmap image
        return heatmap_image


class AnalysisDatabase:
    """Represents a single analysis database, which contains the analysis of attributions."""

    def __init__(self, analysis_path, analysis_method, label_map):
        """
        Initializes a new AnalysisDatabase instance.

        Parameters
        ----------
            analysis_path: str
                The path to the file that contains the analysis database.
            analysis_method: str
                The method that was used for the analysis. Currently only 'spectral_analysis' is supported.
            label_map: LabelMap
                The label map, which contains a mapping between the index of the labels and their human-readable names.

        Raises
        ------
            ValueError
                If the specified analysis method is unknown, a ValueError is raised.
        """

        # Initializes some class members
        self.is_closed = False
        self.analysis_file = None

        # Validates the arguments
        if analysis_method not in ['spectral_analysis']:
            raise ValueError('The specified attribution method {0} is unknown'.format(analysis_method))

        # Stores the arguments for later reference
        self.analysis_path = analysis_path
        self.analysis_method = analysis_method
        self.label_map = label_map

        # Loads the analysis file
        self.analysis_file = h5py.File(self.analysis_path)

    def has_analysis(self, index):
        """
        Determines whether the analysis database contains the analysis with the specified index.

        Parameters
        ----------
            index: int
                The index that is to be checked.

        Raises
        ------
            ValueError
                If the analysis database has already been closed, then a ValueError is raised.

        Returns
        -------
            bool
                Returns True if the database contains the analysis with the specified index and False otherwise.
        """

        if self.is_closed:
            raise ValueError('The analysis database has already been closed.')

        return index in self.analysis_file['index']

    def close(self):
        """Closes the analysis database."""

        if not self.is_closed:
            if self.analysis_file is not None:
                self.analysis_file.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the analysis database."""

        self.close()


class Hdf5Dataset:
    """Represents a dataset that is stored in an HDF5 database."""

    def __init__(self, name, path, label_map):
        """
        Initializes a new Hdf5Dataset instance.

        Parameters
        ----------
            name: str
                The human-readable name of the dataset.
            path: str
                The path to the HDF5 file that contains the dataset.
            label_map: LabelMap
                The label map, which contains a mapping between the index of the labels and their human-readable names.
        """

        # Initializes some class members
        self.is_closed = False
        self.dataset_file = None

        # Stores the arguments for later reference
        self.name = name
        self.path = path
        self.label_map = label_map

        # Loads the dataset itself
        self.dataset_file = h5py.File(self.path)

        # Determines if the dataset allows multiple labels or only single labels (when the dataset is multi-label, then
        # the labels are stored as a boolean NumPy array where the index is the label index and the value determines
        # whether the sample has the label, when the dataset is single-label, then the label is just a scalar value
        # containing the index of the label)
        self.is_multi_label = self.dataset_file['label'][0].dtype == numpy.bool

    def get_sample(self, index):
        """
        Gets the sample at the specified index.

        Parameters
        ----------
            index: int
                The index of the sample that is to be retrieved.

        Raises
        ------
            IndexError
                When the specified index is out of range, a IndexError is raised.

        Returns
        -------
            Sample
                Returns the sample at the specified index.
        """

        # Checks if the dataset is already closed
        if self.is_closed:
            raise ValueError('The dataset is already closed.')

        # Checks if the index is out of range
        if index >= len(self.dataset_file['index']):
            raise IndexError()

        # Extracts the information about the sample from the dataset
        sample_data = self.dataset_file['data'][index]
        sample_label_reference = self.dataset_file['label'][index]
        if self.is_multi_label:
            sample_labels = self.label_map.get_label_from_n_hot_vector(sample_label_reference)
        else:
            sample_labels = [self.label_map.get_label_from_index(sample_label_reference)]

        # Wraps the sample in an object and returns it
        return Sample(index, sample_data, sample_labels)

    def __getitem__(self, key):
        """
        Gets the specified sample(s). This implements the Python interface for the []-indexer.

        Parameters
        ----------
            key: int or slice or range or list or tuple or numpy.ndarray
                The key of the sample/samples that are to be retrieved.

        Raises
        ------
            IndexError
                When the specified index is out of range, a IndexError is raised.

        Returns
        -------
            Sample
                Returns the sample at the specified index.
        """

        # Checks if the key is a slice, in that case it is converted to a range
        if isinstance(key, slice):
            key = range(*key.indices(len(self)))

        # Checks if the key contains multiple indices, in that case all samples for the specified list of indices are
        # retrieved
        if isinstance(key, (range, list, tuple, numpy.ndarray)):
            return [self.get_sample(index) for index in key]

        # If the key is just a single index, the sample is directly retrieved
        return self.get_sample(key)

    def __len__(self):
        """
        Retrieves the number of samples in the dataset. This implements the Python interface for the len() built-in.

        Returns
        -------
            int
                Returns the number of samples in the datasets.
        """

        return len(self.dataset_file['index'])

    def close(self):
        """Closes the dataset."""

        if not self.is_closed:
            if self.dataset_file is not None:
                self.dataset_file.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the dataset."""

        self.close()


class ImageDirectoryDataset:
    """
    Represents a dataset that is stored as image files in a directory hierarchy were the names of the directories
    represent the labels of the images.
    """

    def __init__(self, name, path, label_index_regex, label_word_net_id_regex, label_map):
        """
        Initializes a new ImageDirectoryDataset instance.

        Parameters
        ----------
            path: str
                The path to the HDF5 file that contains the dataset.
            path: str
                The path to the directory that contains the directories for the labels, which in turn contain the images
                that belong to the respective label.
            label_index_regex: str
                A regular expression, which is used to parse the path of a sample for the label index. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or
                label_word_net_id_regex must be specified.
            label_word_net_id_regex: str
                A regular expression, which is used to parse the path of a sample for the WordNet ID. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or
                label_word_net_id_regex must be specified.
            label_map: LabelMap
                The label map, which contains a mapping between the index of the labels and their human-readable names.
        """

        # Initializes some class members
        self.is_closed = False

        # Stores the arguments for later reference
        self.name = name
        self.path = path
        self.label_index_regex = label_index_regex
        self.label_word_net_id_regex = label_word_net_id_regex
        self.label_map = label_map

        # Loads a list of all the paths to all samples in the dataset (they are soreted, because the index of the sorted
        # paths corresponds to the sample index that has to be specified in the get_sample method)
        self.sample_paths = sorted(glob.glob(os.path.join(self.path, '**/*.*'), recursive=True))

    def get_sample(self, index):
        """
        Gets the sample at the specified index.

        Parameters
        ----------
            index: int
                The index of the sample that is to be retrieved.

        Raises
        ------
            IndexError
                When the specified index is out of range, a IndexError is raised.

        Returns
        -------
            Sample
                Returns the sample at the specified index.
        """

        # Checks if the dataset is already closed
        if self.is_closed:
            raise ValueError('The dataset is already closed.')

        # Gets the path to the sample file
        sample_path = self.sample_paths[index]

        # Determines the label of the sample by parsing the path
        if self.label_index_regex is not None:
            match = re.match(self.label_index_regex, sample_path)
            if match:
                label_index = match.groups()[0]
                label = self.label_map.get_label_from_index(label_index)
        else:
            match = re.match(self.label_word_net_id_regex, sample_path)
            if match:
                word_net_id = match.groups()[0]
                label = self.label_map.get_label_from_word_net_id(word_net_id)

        # Loads the image from file
        image = Image.open(sample_path)
        image = numpy.array(image)

        # Returns the sample
        return Sample(index, image, label)

    def __getitem__(self, key):
        """
        Gets the specified sample(s). This implements the Python interface for the []-indexer.

        Parameters
        ----------
            key: int or slice or range or list or tuple or numpy.ndarray
                The key of the sample/samples that are to be retrieved.

        Raises
        ------
            IndexError
                When the specified index is out of range, a IndexError is raised.

        Returns
        -------
            Sample
                Returns the sample at the specified index.
        """

        # Checks if the key is a slice, in that case it is converted to a range
        if isinstance(key, slice):
            key = range(*key.indices(len(self)))

        # Checks if the key contains multiple indices, in that case all samples for the specified list of indices are
        # retrieved
        if isinstance(key, (range, list, tuple, numpy.ndarray)):
            return [self.get_sample(index) for index in key]

        # If the key is just a single index, the sample is directly retrieved
        return self.get_sample(key)

    def __len__(self):
        """
        Retrieves the number of samples in the dataset. This implements the Python interface for the len() built-in.

        Returns
        -------
            int
                Returns the number of samples in the datasets.
        """

        return len(self.sample_paths)

    def close(self):
        """Closes the dataset."""

        if not self.is_closed:
            self.is_closed = True

    def __del__(self):
        """Destructs the dataset."""

        self.close()


class Sample:
    """Represents a sample in a dataset."""

    def __init__(self, index, data, labels):
        """
        Initializes a new Sample instance.

        Parameters
        ----------
            index: int
                The index of the sample within the dataset.
            data: numpy.ndarray
                The data that represents the sample.
            labels: list
                A list of all the labels that the sample has (in a single-label scenario, this list always contains one
                element).
        """

        # Stores the arguments for later use
        self.index = index
        self.data = data
        self.labels = labels

        # Images may come from different sources, e.g. in PyTorch the ordering of the axes is Channels x Width x Height,
        # while in other sources, the ordering is Width x Height x Channel, this code tries to guess which axis
        # represents the RGB channels, and puts them in the order Width x Height x Channel
        if numpy.argmin(self.data.shape) == 0:
            self.data = numpy.moveaxis(self.data, [0, 1, 2], [2, 0, 1])

        # The pixel values of the image may be in three different value ranges: [-1.0, 1.0], [0.0, 1.0], and [0, 255],
        # this code tries to find out which it is and de-normalizes it to the value range of [0, 255], unfortunately, it
        # is not guaranteed that the actual value range of the images has exactly these bounds, because not all images
        # contain pure black or pure white pixels, therefore, a heuristic is used, where the L1 distance between the
        # actual pixel value range and the three value ranges is computed
        actual_pixel_value_range = numpy.array([numpy.min(self.data), numpy.max(self.data)])
        distances = numpy.array([[-1.0, 1.0], [0.0, 1.0], [0.0, 255.0]]) - actual_pixel_value_range
        distances = numpy.abs(numpy.sum(distances, axis=1))
        detected_pixel_value_range_index = numpy.argmin(distances)
        if detected_pixel_value_range_index == 0:
            self.data += 1
            self.data *= 255.0 / 2.0
        elif detected_pixel_value_range_index == 1:
            self.data *= 255.0

        # Finally, the pixel values may be saved as floats and not as integers, so the data type is changed to unsigned
        # 8-bit integers, which is standard for viewing images
        if self.data.dtype != numpy.uint8:
            self.data = self.data.astype(numpy.uint8)


class LabelMap:
    """Represents a map between output neuron indices and their respective human-readable label name."""

    def __init__(self, path):
        """
        Initializes a new LabelMap instance.

        Parameters
        ----------
            path: str
                The path to the label map JSON file.
        """

        # Stores the path to the label map JSON file for later reference
        self.path = path

        # Loads the label map from the specified JSON file
        self.labels = []
        with open(self.path, 'r') as label_map_file:
            for label in json.load(label_map_file):
                self.labels.append(Label(label['index'], label['word_net_id'], label['name']))

    def get_label_from_index(self, index):
        """
        Retrieves the human-readable name of the label with the specified index.

        Parameters
        ----------
            index: int
                The index of the label.

        Raises
        ------
            ValueError
                If the specified index does not exist, then a ValueError is raised.

        Returns
        -------
            str
                Returns the human-readable name of the label.
        """

        for label in self.labels:
            if label.index == index:
                return label.name
        raise ValueError('No label with the specified index {0} could be found.'.format(index))

    def get_labels_from_n_hot_vector(self, n_hot_vector):
        """
        Retrieves the human-readable names of the labels that are specified by the n-hot encoded vector.

        Parameters
        ----------
            n_hot_vector: numpy.ndarray
                A n-hot encoded vector, where the indices are the label indices and the values are True/1 when the label
                is present and False/0 when the label is not present.

        Returns
        -------
            list
                Returns a list of all the labels that are specified by the n-hot encoded vector.
        """

        for index in numpy.argwhere(n_hot_vector):
            yield self.get_label_from_index(index[0])

    def get_label_from_word_net_id(self, word_net_id):
        """
        Retrieves the human-readable name of the label with the specified WordNet ID.

        Parameters
        ----------
            word_net_id: str
                The WordNet ID of the label.

        Raises
        ------
            ValueError
                If the specified WordNet ID does not exist, then a ValueError is raised.

        Returns
        -------
            str
                Returns the human-readable name of the label.
        """

        for label in self.labels:
            if label.word_net_id == word_net_id:
                return label.name
        raise ValueError('No label with the specified WordNet ID {0} could be found.'.format(word_net_id))


class Label:
    """Represents a label of the dataset."""

    def __init__(self, index, word_net_id, name):
        """
        Initializes a new Label instance.

        Parameters
        ----------
            index: int
                The index of the output neuron that corresponds to the label.
            word_net_id: str
                The WordNet ID of the synset that describes the label (this is only necessary for some datasets like
                ImageNet).
            name: str
                The human-readable name of the label.
        """

        self.index = index
        self.word_net_id = word_net_id
        self.name = name


class Workspace:
    """Represents a workspace, which may consist of multiple projects."""

    def __init__(self):
        """Initializes a new Workspace instance."""

        self.is_closed = False
        self.projects = []
        self.current_project = None

    def add_project(self, path):
        """
        Adds a new project to the workspace.

        Parameters
        ----------
            path: str
                The path to the project YAML file.

        Raises
        ------
            ValueError
                If the workspace is already closed, a ValueError is raised.
        """

        if self.is_closed:
            raise ValueError('The workspace is already closed.')

        self.projects.append(Project(path))
        if self.current_project is None:
            self.current_project = self.projects[0]

    def get_project_names(self):
        """
        Retrieves the names of all the loaded projects.

        Returns
        -------
            list
                Returns a list of the names of all loaded projects.

        Raises
        ------
            ValueError
                If the workspace is already closed, a ValueError is raised.
        """

        if self.is_closed:
            raise ValueError('The workspace is already closed.')

        for project in self.projects:
            yield project.name

    def select_project(self, name):
        """
        Selects the current project by name.

        Parameters
        ----------
            name: str
                The name of the project that is to be selected as the current project.

        Raises
        ------
            ValueError
                If the workspace is already closed, a ValueError is raised.
                If the project with the specified name could not be found, then a ValueError is raised.

        Returns
        -------
            Project
                Returns the selected project.
        """

        # If the workspace is closed, then no projects can be selected
        if self.is_closed:
            raise ValueError('The workspace is already closed.')

        # Searches for the project that is to be selected and selects it
        for project in self.projects:
            if project.name == name:
                self.current_project = project
                return project

        # If a project with the specified name could not be found, then an exception is raised
        raise ValueError('The project with the name "{0}" could not be found.'.format(name))

    def get_current_project(self):
        """
        Retrieves the current selected project.

        Returns
        -------
            Project
                Returns the currently selected project.
        """

        return self.current_project

    def close(self):
        """Closes the workspace and all projects within it."""

        if not self.is_closed:
            for project in self.projects:
                project.close()
            self.current_project = None
            self.is_closed = True

    def __del__(self):
        """Destructs the workspace."""

        self.close()
