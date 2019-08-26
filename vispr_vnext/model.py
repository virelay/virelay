"""Contains the data model abstraction."""

import os
import re
import json
import glob

import yaml
import h5py
import numpy
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

                # Loads the dataset of the project
                dataset_type = project['dataset']['type']
                if dataset_type == 'hdf5':
                    self.dataset = Hdf5Dataset(
                        project['dataset']['name'],
                        os.path.join(working_directory, project['dataset']['path']),
                        os.path.join(working_directory, project['dataset']['label_map'])
                    )
                elif dataset_type == 'image_directory':
                    self.dataset = ImageDirectoryDataset(
                        project['dataset']['name'],
                        os.path.join(working_directory, project['dataset']['path']),
                        os.path.join(working_directory, project['dataset']['label_map']),
                        project['dataset']['label_index_regex'],
                        project['dataset']['label_word_net_id_regex']
                    )
                else:
                    raise ValueError('The specified dataset type "{0}" is unknown.'.format(dataset_type))

                # Loads the attributions of the project
                for attribution in project['attributions']:
                    self.attributions.append(Attribution(
                        os.path.join(working_directory, attribution['attribution']),
                        attribution['attribution_method'],
                        attribution['attribution_strategy']
                    ))

                # Loads the analyses of the project
                for analysis in project['analyses']:
                    self.analyses.append(Analysis(
                        os.path.join(working_directory, analysis['analysis']),
                        analysis['analysis_method']
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


class Attribution:
    """Represents a single attribution database, which contains the attributions for the dataset samples."""

    def __init__(self, attribution_path, attribution_method, attribution_strategy):
        """
        Initializes a new Attribution instance.

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

        # Loads the attribution files
        self.attribution_file = h5py.File(self.attribution_path)

    def close(self):
        """Closes the attribution database."""

        if not self.is_closed:
            if self.attribution_file is not None:
                self.attribution_file.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the attribution database."""

        self.close()


class Analysis:
    """Represents a single analysis database, which contains the analysis of attributions."""

    def __init__(self, analysis_path, analysis_method):
        """
        Initializes a new Analysis instance.

        Parameters
        ----------
            analysis_path: str
                The path to the file that contains the analysis database.
            analysis_method: str
                The method that was used for the analysis. Currently only 'spectral_analysis' is supported.

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

        # Loads the analysis file
        self.analysis_file = h5py.File(self.analysis_path)

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

    def __init__(self, name, path, label_map_path):
        """
        Initializes a new Hdf5Dataset instance.

        Parameters
        ----------
            name: str
                The human-readable name of the dataset.
            path: str
                The path to the HDF5 file that contains the dataset.
            label_map_path: str
                The path to the JSON file that contains a mapping between the index of the labels and their
                human-readable names.
        """

        # Initializes some class members
        self.is_closed = False
        self.dataset_file = None

        # Stores the arguments for later reference
        self.name = name
        self.path = path

        # Loads the label map
        self.label_map = LabelMap(label_map_path)

        # Loads the dataset itself
        self.dataset_file = h5py.File(self.path)

        # Determines if the dataset is allows multiple labels or only single labels (when the dataset is multi-label,
        # then the labels are stored as a boolean NumPy array where the index is the label index and the value
        # determines whether the sample has the label, when the dataset is single-label, then the label is just a scalar
        # value containing the index of the label)
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
        sample_labels = []
        if self.is_multi_label:
            for index in numpy.argwhere(sample_label_reference):
                sample_labels.append(self.label_map.get_label_by_index(index[0]))
        else:
            sample_labels.append(self.label_map.get_label_by_index(sample_label_reference))

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

    def __init__(
            self,
            name,
            path,
            label_map_path,
            label_index_regex,
            label_word_net_id_regex
    ):
        """
        Initializes a new ImageDirectoryDataset instance.

        Parameters
        ----------
            path: str
                The path to the HDF5 file that contains the dataset.
            path: str
                The path to the directory that contains the directories for the labels, which in turn contain the images
                that belong to the respective label.
            label_map_path: str
                The path to the JSON file that contains a mapping between the index of the labels and their
                human-readable names.
            label_index_regex: str
                A regular expression, which is used to parse the path of a sample for the label index. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or
                label_word_net_id_regex must be specified.
            label_word_net_id_regex: str
                A regular expression, which is used to parse the path of a sample for the WordNet ID. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or
                label_word_net_id_regex must be specified.
        """

        # Initializes some class members
        self.is_closed = False

        # Stores the arguments for later reference
        self.name = name
        self.path = path
        self.label_map_path = label_map_path
        self.label_index_regex = label_index_regex
        self.label_word_net_id_regex = label_word_net_id_regex

        # Loads the label map
        self.label_map = LabelMap(label_map_path)

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
                label = self.label_map.get_label_by_index(label_index)
        else:
            match = re.match(self.label_word_net_id_regex, sample_path)
            if match:
                word_net_id = match.groups()[0]
                label = self.label_map.get_label_by_word_net_id(word_net_id)

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
        if numpy.argmax(self.data.shape) == 2:
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

    def get_label_by_index(self, index):
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

    def get_label_by_word_net_id(self, word_net_id):
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
