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

        Parameters:
        -----------
            path: str
                The path to the YAML file that contains the project definition.

        Exceptions:
        -----------
            ValueError:
                If the project file is incorrect or corrupted, a ValueError is raised.
                If the specified dataset type is unknown, then a ValueError is raised.
        """

        # Initializes some class members
        self.is_closed = False

        # Stores the path for later reference
        self.path = path

        # Loads the project from the YAML file
        working_directory = os.path.dirname(self.path)
        with open(self.path, 'r') as project_file:
            try:
                project = yaml.safe_load(project_file)['project']
                self.name = project['name']
                dataset_type = project['dataset']['type']
                dataset_path = os.path.join(working_directory, project['dataset']['path'])
                dataset_label_map_path = os.path.join(working_directory, project['dataset']['label_map'])
                if dataset_type == 'hdf5':
                    is_multi_label = project['dataset']['is_multi_label']
                    self.dataset = Hdf5Dataset(dataset_path, dataset_label_map_path, is_multi_label)
                elif dataset_type == 'image_directory':
                    sample_file_glob = project['dataset']['sample_file_glob']
                    label_index_regex = project['dataset']['label_index_regex']
                    label_word_net_id_regex = project['dataset']['label_word_net_id_regex']
                    self.dataset = ImageDirectoryDataset(
                        dataset_path,
                        dataset_label_map_path,
                        sample_file_glob,
                        label_index_regex,
                        label_word_net_id_regex
                    )
                else:
                    raise ValueError('The specified dataset type "{0}" is unknown.'.format(dataset_type))
                self.sources = []
                for source in project['sources']:
                    self.sources.append(Source(
                        os.path.join(working_directory, source['attribution']),
                        os.path.join(working_directory, source['analysis'])
                    ))
            except yaml.YAMLError:
                raise ValueError('An error occurred while loading the project file.')

    def close(self):
        """Closes the project, its dataset, and all of its sources."""

        if not self.is_closed:
            self.dataset.close()
            for source in self.sources:
                source.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the project."""

        self.close()


class Source:
    """Represents a combination of an attribution database and an analysis database."""

    def __init__(self, attribution_path, analysis_path):
        """
        Initializes a new Source instance.

        Parameters:
        -----------
            attribution_path: str
                The path to the file that contains the attribution database.
            analysis_path: str
                The path to the file that contains the analysis database.
        """

        # Initializes some class members
        self.is_closed = False

        # Stores the paths to the attribution and analysis files for later reference
        self.attribution_path = attribution_path
        self.analysis_path = analysis_path

    def close(self):
        """Closes the source."""

        if not self.is_closed:
            self.is_closed = True

    def __del__(self):
        """Destructs the source."""

        self.close()


class Hdf5Dataset:
    """Represents a dataset that is stored in an HDF5 database."""

    def __init__(self, path, label_map_path, is_multi_label):
        """
        Initializes a new Hdf5Dataset instance.

        Parameters:
        -----------
            path: str
                The path to the HDF5 file that contains the dataset.
            label_map_path: str
                The path to the JSON file that contains a mapping between the index of the labels and their
                human-readable names.
            is_multi_label: bool
                Determines whether the samples of the dataset can have multiple labels.
        """

        # Stores the arguments for later reference
        self.path = path
        self.is_multi_label = is_multi_label

        # Initializes some class members
        self.is_closed = False

        # Loads the label map
        self.label_map = LabelMap(label_map_path)

        # Loads the dataset itself
        self.dataset_file = h5py.File(self.path)

    def get_sample(self, index):
        """
        Gets the sample at the specified index.

        Parameters:
        -----------
            index: int
                The index of the sample that is to be retrieved.

        Exceptions:
        -----------
            IndexError:
                When the specified index is out of range, a IndexError is raised.

        Returns:
        --------
            Sample:
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

    def close(self):
        """Closes the dataset."""

        if not self.is_closed:
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
            path,
            label_map_path,
            sample_file_glob,
            label_index_regex,
            label_word_net_id_regex
    ):
        """
        Initializes a new ImageDirectoryDataset instance.

        Parameters:
        -----------
            path: str
                The path to the directory that contains the directories for the labels, which in turn contain the images
                that belong to the respective label.
            label_map_path: str
                The path to the JSON file that contains a mapping between the index of the labels and their
                human-readable names.
            sample_file_glob: str
                A glob pattern that is used to retrieve an image from the dataset directory by index. The placeholder
                '{index}' can be used to specify where the sample index should be placed.
            label_index_regex: str
                A regular expression, which is used to parse the path of a sample for the label index. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or
                label_word_net_id_regex must be specified.
            label_word_net_id_regex: str
                A regular expression, which is used to parse the path of a sample for the WordNet ID. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or
                label_word_net_id_regex must be specified.
        """

        # Stores the arguments for later reference
        self.path = path
        self.label_map_path = label_map_path
        self.sample_file_glob = sample_file_glob
        self.label_index_regex = label_index_regex
        self.label_word_net_id_regex = label_word_net_id_regex

        # Initializes some class members
        self.is_closed = False

        # Loads the label map
        self.label_map = LabelMap(label_map_path)

    def get_sample(self, index):
        """
        Gets the sample at the specified index.

        Parameters:
        -----------
            index: int
                The index of the sample that is to be retrieved.

        Exceptions:
        -----------
            IndexError:
                When the specified index is out of range, a IndexError is raised.

        Returns:
        --------
            Sample:
                Returns the sample at the specified index.
        """

        # Checks if the dataset is already closed
        if self.is_closed:
            raise ValueError('The dataset is already closed.')

        # Finds the path to the file that contains the sample
        glob_pattern = self.sample_file_glob.replace('{index}', str(index))
        sample_path_candidates = glob.glob(os.path.join(self.path, glob_pattern))
        if len(sample_path_candidates) != 1:
            raise IndexError()
        sample_path = sample_path_candidates[0]

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

        Parameters:
        -----------
            index: int
                The index of the sample within the dataset.
            data: numpy.ndarray
                The data that represents the sample.
            labels: list
                A list of all the labels that the sample has (in a single-label scenario, this list always contains one
                element).
        """

        self.index = index
        self.data = data
        self.labels = labels


class LabelMap:
    """Represents a map between output neuron indices and their respective human-readable label name."""

    def __init__(self, path):
        """
        Initializes a new LabelMap instance.

        Parameters:
        -----------
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

        Parameters:
        -----------
            index: int
                The index of the label.

        Exception:
        ----------
            ValueError:
                If the specified index does not exist, then a ValueError is raised.

        Returns:
        --------
            str:
                Returns the human-readable name of the label.
        """

        for label in self.labels:
            if label.index == index:
                return label.name
        raise ValueError('No label with the specified index {0} could be found.'.format(index))

    def get_label_by_word_net_id(self, word_net_id):
        """
        Retrieves the human-readable name of the label with the specified WordNet ID.

        Parameters:
        -----------
            word_net_id: str
                The WordNet ID of the label.

        Exception:
        ----------
            ValueError:
                If the specified WordNet ID does not exist, then a ValueError is raised.

        Returns:
        --------
            str:
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

        Parameters:
        -----------
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

        self.projects = []
        self.current_project = None
        self.is_closed = False

    def add_project(self, path):
        """
        Adds a new project to the workspace.

        Parameters:
        -----------
            path: str
                The path to the project YAML file.

        Exceptions:
        -----------
            ValueError:
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

        Returns:
        --------
            list
                Returns a list of the names of all loaded projects.

        Exceptions:
        -----------
            ValueError:
                If the workspace is already closed, a ValueError is raised.
        """

        if self.is_closed:
            raise ValueError('The workspace is already closed.')

        for project in self.projects:
            yield project.name

    def select_project(self, name):
        """
        Selects the current project by name.

        Parameters:
        -----------
            name: str
                The name of the project that is to be selected as the current project.

        Exceptions:
        -----------
            ValueError:
                If the workspace is already closed, a ValueError is raised.
                If the project with the specified name could not be found, then a ValueError is raised.

        Returns:
        --------
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

        Returns:
        --------
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
