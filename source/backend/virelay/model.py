"""Contains the data model abstraction."""

import os
import re
import json
import glob
from dataclasses import dataclass
from typing import Literal, TypeAlias, overload, TypedDict

import yaml
import h5py
import numpy
from PIL import Image
from numpy.typing import NDArray

from virelay.image_processing import add_border, center_crop, render_heatmap, render_superimposed_heatmap


DownSamplingMethod: TypeAlias = Literal['none', 'center_crop', 'resize']
"""Represents the different methods that can be used to down-sample an image."""


UpSamplingMethod: TypeAlias = Literal['none', 'fill_zeros', 'fill_ones', 'edge_repeat', 'mirror_edge', 'wrap_around', 'resize']
"""Represents the different methods that can be used to up-sample an image."""


AttributionStrategy: TypeAlias = Literal['true_label', 'predicted_label']
"""The different possible attribution strategies."""


DatasetType: TypeAlias = Literal['hdf5', 'image_directory']
"""The different possible dataset types."""


class Project:
    """Represents a single project, which can be loaded from a YAML file."""

    def __init__(self, path: str) -> None:
        """Initializes a new Project instance.

        Args:
            path (str): The path to the YAML file that contains the project definition.

        Raises:
            ValueError: If the project file is incorrect or corrupted, a ValueError is raised. If the specified dataset type is unknown, then a
                ValueError is raised.
        """

        # Initializes some class members
        self.name: str
        self.model: str
        self.path: str = path
        self.is_closed: bool
        self.label_map: LabelMap
        self.dataset: Hdf5Dataset | ImageDirectoryDataset
        self.attribution_method: str
        self.attribution_strategy: AttributionStrategy
        self.attributions: list[AttributionDatabase] = []
        self.analyses: dict[str, list[AnalysisDatabase]] = {}

        # Loads the project from the YAML file; the project is initialized as being closed and the is_closed flag is only set to False after the file
        # has been successfully loaded; this is done to prevent an exception from occurring in the destructor if in an exception is raised during the
        # loading of the file (the destructor would check if the file is closed and try to close it, but since the exception occurs before the
        # dataset, attributions, and analyses properties are assigned, an AttributeError would be raised; if we were to initialize the dataset,
        # attributions, and analyses properties with None, we would have to check for None everywhere to satisfy the type checker, which is not very
        # elegant)
        self.is_closed = True
        working_directory = os.path.dirname(self.path)
        with open(self.path, 'r', encoding='utf-8') as project_yaml_file:
            try:

                # Loads the project and extracts some general information
                project_file: ProjectFileYaml = yaml.safe_load(project_yaml_file)
                project: ProjectYaml = project_file['project']
                self.name = project['name']
                self.model = project['model']

                # Loads the label map, which is used to get the human-readable names of the labels referenced in the dataset as well as in the
                # attributions and analyses databases
                self.label_map = LabelMap(os.path.join(working_directory, project['label_map']))

                # Loads the dataset of the project
                if 'dataset' not in project:
                    raise ValueError('The project file does not contain a dataset.')
                if project['dataset']['type'] == 'hdf5':
                    self.dataset = Hdf5Dataset(
                        project['dataset']['name'],
                        os.path.join(working_directory, project['dataset']['path']),
                        self.label_map
                    )
                elif project['dataset']['type'] == 'image_directory':
                    self.dataset = ImageDirectoryDataset(
                        project['dataset']['name'],
                        os.path.join(working_directory, project['dataset']['path']),
                        project['dataset']['label_index_regex'],
                        project['dataset']['label_word_net_id_regex'],
                        project['dataset']['input_width'],
                        project['dataset']['input_height'],
                        project['dataset']['down_sampling_method'],
                        project['dataset']['up_sampling_method'],
                        self.label_map
                    )
                else:
                    raise ValueError('The specified dataset type is unknown.')

                # Loads the attributions of the project
                if 'attributions' in project:
                    self.attribution_method = project['attributions']['attribution_method']
                    self.attribution_strategy = project['attributions']['attribution_strategy']
                    for attribution_database in project['attributions']['sources']:
                        self.attributions.append(AttributionDatabase(
                            os.path.join(working_directory, attribution_database),
                            self.label_map
                        ))

                # Loads the analyses of the project
                if 'analyses' in project:
                    for analysis in project['analyses']:
                        analysis_method = analysis['analysis_method']
                        if analysis_method not in self.analyses:
                            self.analyses[analysis_method] = []
                        for analysis_database in analysis['sources']:
                            self.analyses[analysis_method].append(AnalysisDatabase(
                                os.path.join(working_directory, analysis_database),
                                self.label_map
                            ))

                # After the project file was loaded successfully, the project is not closed anymore
                self.is_closed = False

            except yaml.YAMLError as yaml_error:
                raise ValueError('An error occurred while loading the project file.') from yaml_error

    def get_sample(self, index: int) -> 'Sample':
        """Retrieves the sample from the dataset with the specified index.

        Args:
            index (int): The index of the dataset sample.

        Raises:
            ValueError: If the project has already been closed, then a ValueError is raised. If the project does not contain a dataset, then a
                ValueError is raised.

        Returns:
            Sample: Returns the dataset sample with the specified index.
        """

        if self.is_closed:
            raise ValueError('The project has already been closed.')

        return self.dataset.get_sample(index)

    def get_attribution(self, index: int) -> 'Attribution':
        """Retrieves the attribution for the specified index.

        Args:
            index (int): The index of the attribution.

        Raises:
            ValueError: If the project has already been closed, then a ValueError is raised.
            LookupError: If no attribution with the specified index could be found, then a LookupError is raised

        Returns:
            Attribution: Returns the attribution with the specified index.
        """

        if self.is_closed:
            raise ValueError('The project has already been closed.')

        for attribution_database in self.attributions:
            if attribution_database.has_attribution(index):
                return attribution_database.get_attribution(index)

        raise LookupError(f'No attribution with the specified index {index} could be found.')

    def get_analysis_methods(self) -> list[str]:
        """Retrieves the names of all the analysis methods that are in this project.

        Raises:
            ValueError: If the project has already been closed, then a ValueError is raised.

        Returns:
            list[str]: Returns a list of the names of the all the analysis methods in this project.
        """

        if self.is_closed:
            raise ValueError('The project has already been closed.')

        return list(self.analyses.keys())

    def get_analysis_categories(self, analysis_method: str) -> list['AnalysisCategory']:
        """Retrieves the names of the categories that are in the analyses of the specified analysis method.

        Args:
            analysis_method (str): The name of the analysis method for which the categories are to be retrieved.

        Raises:
            ValueError: If the project has already been closed, then a ValueError is raised.
            LookupError: If the specified analysis method does not exist, then a LookupError is raised.

        Returns:
            list[AnalysisCategory]: Returns a list of the names of the categories.
        """

        if self.is_closed:
            raise ValueError('The project has already been closed.')

        if analysis_method not in self.analyses:
            raise LookupError(f'The specified analysis method "{analysis_method}" could not be found.')

        categories: list[AnalysisCategory] = []
        for analysis in self.analyses[analysis_method]:
            for category in analysis.get_categories():
                if category.name not in map(lambda c: c.name, categories):
                    categories.append(category)

        return categories

    def get_analysis_clustering_names(self, analysis_method: str) -> list[str]:
        """Retrieves the names of the clustering methods that are in the analyses of the specified analysis method.

        Args:
            analysis_method (str): The name of the analysis method for which the clusterings are to be retrieved.

        Raises:
            ValueError: If the project has already been closed, then a ValueError is raised.
            LookupError: If the specified analysis method does not exist, then a LookupError is raised.

        Returns:
            list[str]: Returns a list of the names of the clusterings.
        """

        if self.is_closed:
            raise ValueError('The project has already been closed.')

        if analysis_method not in self.analyses:
            raise LookupError(f'The specified analysis method "{analysis_method}" could not be found.')

        return self.analyses[analysis_method][0].get_clustering_names()

    def get_analysis_embedding_names(self, analysis_method: str) -> list[str]:
        """Retrieves the names of the embedding methods that are in the analyses of the specified analysis method.

        Args:
            analysis_method (str): The name of the analysis method for which the embeddings are to be retrieved.

        Raises:
            ValueError: If the project has already been closed, then a ValueError is raised.
            LookupError: If the specified analysis method does not exist, then a LookupError is raised.

        Returns:
            list[str]: Returns a list of the names of the embeddings.
        """

        if self.is_closed:
            raise ValueError('The project has already been closed.')

        if analysis_method not in self.analyses:
            raise LookupError(f'The specified analysis method "{analysis_method}" could not be found.')

        return self.analyses[analysis_method][0].get_embedding_names()

    def get_analysis(self, analysis_method: str, category_name: str, clustering_name: str, embedding_name: str) -> 'Analysis':
        """Retrieves a complete analysis.

        Args:
            analysis_method (str): The name of the analysis method from which the analysis is to be retrieved.
            category_name (str): The name of the category for which the analysis was performed. Each analysis was performed for a certain subset of
                the attributions, in most cases this subset will be defined by the label of dataset samples of the attributions. So the category name
                is the umbrella term for all the attributions that comprise the analysis, which will, in most cases, be the name of the label.
            clustering_name (str): On top of the embedding a clustering is performed. This clustering name is the name of the clustering that is to be
                retrieved (because usually the analysis contains multiple different clusterings, which are most likely k-means with different k's).
            embedding_name (str): The name of the embedding that is to be retrieved. This is the name of the method that was used to create the
                embedding. Most likely this will be "spectral" for spectral embeddings and "tsne" for a T-SNE embedding.

        Raises:
            ValueError: If the project has already been closed, then a ValueError is raised.
            LookupError: When the analysis for the specified analysis method, category name, clustering name, and embedding name could not be found,
                then a LookupError is raised.

        Returns:
            Analysis: Returns the analysis for the specified name.
        """

        if self.is_closed:
            raise ValueError('The project has already been closed.')

        if analysis_method not in self.analyses:
            raise LookupError(f'The specified analysis method "{analysis_method}" could not be found.')

        for analysis_database in self.analyses[analysis_method]:
            if analysis_database.has_analysis(category_name, clustering_name, embedding_name):
                return analysis_database.get_analysis(category_name, clustering_name, embedding_name)

        raise LookupError(
            f'No analysis in the category "{category_name}" with the clustering "{clustering_name}" and embedding '
            f'"{embedding_name}" could be found.'
        )

    def close(self) -> None:
        """Closes the project, its dataset, and all of its sources."""

        if not self.is_closed:
            self.dataset.close()
            for attribution in self.attributions:
                attribution.close()
            self.attributions = []
            for _, analyses in self.analyses.items():
                for analysis in analyses:
                    analysis.close()
            self.analyses = {}
            self.is_closed = True

    def __del__(self) -> None:
        """Destructs the project."""

        self.close()


class AttributionDatabase:
    """Represents a single attribution database, which contains the attributions for the dataset samples."""

    def __init__(self, attribution_path: str, label_map: 'LabelMap') -> None:
        """Initializes a new AttributionDatabase instance.

        Args:
            attribution_path (str): The path to the file that contains the attribution database.
            label_map (LabelMap): The label map, which contains a mapping between the index of the labels and their human-readable names.
        """

        # Stores the arguments for later reference
        self.attribution_path: str = attribution_path
        self.label_map: LabelMap = label_map

        # Loads the attribution files; the attribution database is initialized as being closed and the is_closed flag is only set to False after the
        # file has been successfully loaded; this is done to prevent an exception from occurring in the destructor if in an exception is raised during
        # the loading of the file (the destructor would check if the file is closed and try to close it, but since the exception occurs before the
        # attribution_file property is assigned, an AttributeError would be raised; if we were to initialize the attribution_file property with None,
        # we would have to check for None everywhere to satisfy the type checker, which is not very elegant)
        self.is_closed: bool = True
        self.attribution_file: h5py.File = h5py.File(self.attribution_path, 'r')
        self.is_closed = False

        # Determines if the dataset allows multiple labels or only single labels (when the dataset is multi-label, then the labels are stored as a
        # boolean NumPy array where the index is the label index and the value determines whether the sample has the label, when the dataset is
        # single-label, then the label is just a scalar value containing the index of the label)
        self.is_multi_label: bool = False
        labels: h5py.Group | h5py.Dataset = self.attribution_file['label']
        if isinstance(labels, h5py.Dataset):
            self.is_multi_label = labels.dtype == numpy.bool
        if isinstance(labels, h5py.Group):
            self.is_multi_label = labels[list(labels.keys())[0]].dtype == numpy.bool

    def has_attribution(self, index: int) -> bool:
        """Determines whether the attribution database contains the attribution with the specified index.

        Args:
            index (int): The index that is to be checked.

        Raises:
            ValueError: If the attribution database has already been closed, then a ValueError is raised.

        Returns:
            bool: Returns True if the database contains the attribution with the specified index and False otherwise.
        """

        if self.is_closed or self.attribution_file is None:
            raise ValueError('The attribution database has already been closed.')

        if 'index' in self.attribution_file.keys():
            return index in self.attribution_file['index']
        attributions: h5py.Dataset | h5py.Group = self.attribution_file['attribution']
        if isinstance(attributions, h5py.Dataset):
            number_of_attributions: int = self.attribution_file['attribution'].shape[0]
        else:
            number_of_attributions = len(attributions)
        return index < number_of_attributions

    def get_attribution(self, index: int) -> 'Attribution':
        """Gets the attribution with the specified index.

        Args:
            index (int): The index of the attribution that is to be retrieved.

        Raises:
            ValueError: If the attribution database has already been closed, then a ValueError is raised.
            LookupError: When the no attribution with the specified index exists, then an LookupError is raised.

        Returns:
            Attribution: Returns the attribution with the specified index.
        """

        # Checks if the attribution database has already been closed, if so, a ValueError is raised
        if self.is_closed or self.attribution_file is None:
            raise ValueError('The attribution database has already been closed.')

        # Checks if the specified attribution exists, if not, then an LookupError is raised
        if not self.has_attribution(index):
            raise LookupError(f'No attribution with the index {index} could be found.')

        # Check where the searched index is in the attribution file
        original_index = index
        if 'index' in self.attribution_file:
            index = numpy.where(index == self.attribution_file['index'][:])[0][0].item()

        # Extracts the attribution data from the HDF5 file
        attributions: h5py.Dataset | h5py.Group = self.attribution_file['attribution']
        if isinstance(attributions, h5py.Dataset):
            attribution_data = attributions[index]
        else:
            attribution_data = attributions[list(attributions.keys())[index]][:]

        # Extracts the predictions from the HDF5 file
        predictions: h5py.Dataset | h5py.Group = self.attribution_file['prediction']
        if isinstance(predictions, h5py.Dataset):
            attribution_prediction = predictions[index]
        else:
            attribution_prediction = predictions[list(predictions.keys())[index]][:]

        # Extracts the labels from the HDF5 file
        labels: h5py.Dataset | h5py.Group = self.attribution_file['label']
        if isinstance(labels, h5py.Dataset):
            attribution_label_reference = labels[index]
        else:
            attribution_label_reference = labels[list(labels.keys())[index]]
        attribution_labels = self.label_map.get_labels(attribution_label_reference)

        # Wraps the attribution in an object and returns it
        return Attribution(
            original_index,
            attribution_data,
            attribution_labels,
            attribution_prediction
        )

    def close(self) -> None:
        """Closes the attribution database."""

        if not self.is_closed:
            self.attribution_file.close()
            self.attribution_file = None
            self.is_closed = True

    def __del__(self) -> None:
        """Destructs the attribution database."""

        self.close()


class Attribution:
    """Represents a single attribution from an attribution database."""

    def __init__(self, index: int, data: NDArray[numpy.float64], labels: 'Label | list[Label]', prediction: NDArray[numpy.float64]) -> None:
        """Initializes a new Attribution instance.

        Args:
            index (int): The index of the attribution, which is the index of the sample for which the attribution was created.
            data (NDArray[numpy.float64]): The attribution data, which is a raw heatmap.
            labels (Label | list[Label]): The ground truth label or a list of the ground truth labels of the sample for which the attribution was
                created.
            prediction (NDArray[numpy.float64]): The original output of the model.
        """

        # Stores the parameters for later use
        self.index: int = index
        self.data: NDArray[numpy.float64] = data
        if not isinstance(labels, list):
            labels = [labels]
        self.labels: list[Label] = labels
        self.prediction: NDArray[numpy.float64] = prediction

        # Heatmaps (the attribution data) may come from different sources, e.g. in PyTorch the ordering of the axes is Channels x Width x Height,
        # while in other sources, the ordering is Width x Height x Channel, this code tries to guess which axis represents the RGB channels, and puts
        # them in the order Width x Height x Channel
        if numpy.argmin(self.data.shape) == 0:
            self.data = numpy.moveaxis(self.data, [0, 1, 2], [2, 0, 1])

    def render_heatmap(self, color_map: str, image_to_superimpose: NDArray[numpy.float64] | None = None) -> NDArray[numpy.float64]:
        """Takes the raw attribution data and converts it so that the data can be visualized as a heatmap.

        Args:
            color_map (str): The name of color map that is to be used to render the heatmap.
            image_to_superimpose (NDArray[numpy.float64] | None): An optional image onto which the heatmap should be superimposed. Defaults to None.

        Returns:
            NDArray[numpy.float64]: Returns the rendered heatmap.
        """

        if image_to_superimpose is not None:
            return render_superimposed_heatmap(self.data, image_to_superimpose, color_map)
        return render_heatmap(self.data, color_map)


class AnalysisDatabase:
    """Represents a single analysis database, which contains the analysis of attributions."""

    def __init__(self, analysis_path: str, label_map: 'LabelMap') -> None:
        """Initializes a new AnalysisDatabase instance.

        Args:
            analysis_path (str): The path to the file that contains the analysis database.
            label_map (LabelMap): The label map, which contains a mapping between the index of the labels and their human-readable names.
        """

        # Stores the arguments for later reference
        self.analysis_path: str = analysis_path
        self.label_map: LabelMap = label_map

        # Loads the analysis file; the analysis database is initialized as being closed and the is_closed flag is only set to False after the file
        # has been successfully loaded; this is done to prevent an exception from occurring in the destructor if in an exception is raised during the
        # loading of the file (the destructor would check if the file is closed and try to close it, but since the exception occurs before the
        # analysis_file property is assigned, an AttributeError would be raised; if we were to initialize the analysis_file property with None, we
        # would have to check for None everywhere to satisfy the type checker, which is not very elegant)
        self.is_closed: bool = True
        self.analysis_file: h5py.File = h5py.File(self.analysis_path, 'r')
        self.is_closed = False

    def get_categories(self) -> list['AnalysisCategory']:
        """Retrieves the names of all the categories that are contained in this analysis database. The category names are umbrella terms for the
        attributions for which the analysis was performed. In most cases this will be the name/index/WordNet ID of the label of the dataset samples of
        the attributions.

        Raises:
            ValueError: If the analysis database has already been closed, then a ValueError is raised.

        Returns:
            list[AnalysisCategory]: Returns a list containing all the categories that are contained in this analysis database.
        """

        if self.is_closed or self.analysis_file is None:
            raise ValueError('The analysis database has already been closed.')

        categories = []
        for category_name in self.analysis_file.keys():
            try:
                human_readable_category_name = self.label_map.get_label_names(category_name)
            except LookupError:
                human_readable_category_name = ''
            categories.append(AnalysisCategory(category_name, human_readable_category_name))

        return categories

    def get_clustering_names(self) -> list[str]:
        """Retrieves the names of all the clusterings that are contained in this analysis database. The clustering names are usually the name of the
        method with which the clustering was generated. Most likely this will be k-means with a specific value for k, e.g. 'kmeans-10'.

        Raises:
            ValueError: If the analysis database has already been closed, then a ValueError is raised.

        Returns:
            list[str]: Returns a list containing the names of all the clusterings that are contained in this analysis database.
        """

        # Checks if the database has already been closed, in that case a ValueError is raised
        if self.is_closed or self.analysis_file is None:
            raise ValueError('The analysis database has already been closed.')

        # Since every analysis contained in this analysis database has its own set of clusterings, the number and the names of the clusterings may
        # vary between analyses, as it is not enforced that they all must have the same clusterings, nevertheless, this assumes that each analysis in
        # a single analysis database has the same clusterings and therefore the names are only retrieved from the first one
        first_category_name = self.get_categories()[0].name
        return list(self.analysis_file[first_category_name]['cluster'])

    def get_embedding_names(self) -> list[str]:
        """Retrieves the names of all the embeddings that are contained in the analysis database. The embedding names are the names of the methods
        with which the embedding was generated. This will most likely be "spectral" for spectral embeddings and "tsne" for a T-SNE embedding.

        Raises:
            ValueError: If the analysis database has already been closed, then a ValueError is raised.

        Returns:
            list[str]: Returns a list containing the names of all the embeddings that are contained in this analysis database.
        """

        # Checks if the database has already been closed, in that case a ValueError is raised
        if self.is_closed or self.analysis_file is None:
            raise ValueError('The analysis database has already been closed.')

        # Since every analysis contained in this analysis database has its own set of embeddings, the number and the names of the embeddings may vary
        # between analyses, as it is not enforced that they all must have the same embeddings, nevertheless, this assumes that each analysis in a
        # single analysis database has the same embeddings and therefore the names are only retrieved from the first one
        first_category_name = self.get_categories()[0].name
        return list(self.analysis_file[first_category_name]['embedding'])

    def has_analysis(self, category_name: str, clustering_name: str, embedding_name: str) -> bool:
        """Determines whether the analysis database contains the analysis with the specified category name (categories can, for example, be classes
        for which the analysis was performed).

        Args:
            category_name (str): The name of the category for which the analysis was performed. Each analysis was performed for a certain subset of
                the attributions, in most cases this subset will be defined by the label of dataset samples of the attributions. So the category name
                is the umbrella term for all the attributions that comprise the analysis, which will, in most cases, be the name/index/WordNet ID of
                the label.
            clustering_name (str): On top of the embedding a clustering is performed. This clustering name is the name of the clustering that is to be
                retrieved (because usually the analysis contains multiple different clusterings, which are most likely k-means with different k's).
            embedding_name (str): The name of the embedding that is to be retrieved. This is the name of the method that was used to create the
                embedding. Most likely this will be "spectral" for spectral embeddings and "tsne" for a T-SNE embedding.

        Raises:
            ValueError: If the analysis database has already been closed, then a ValueError is raised.

        Returns:
            bool: Returns True if the database contains the analysis with the specified name and False otherwise.
        """

        if self.is_closed or self.analysis_file is None:
            raise ValueError('The analysis database has already been closed.')

        if category_name not in self.analysis_file.keys():
            return False
        if clustering_name not in self.analysis_file[category_name]['cluster'].keys():
            return False
        return embedding_name in self.analysis_file[category_name]['embedding'].keys()

    def get_analysis(self, category_name: str, clustering_name: str, embedding_name: str) -> 'Analysis':
        """Gets the analysis for the specified name (names can be, for example, classes for which the analysis was performed).

        Args:
            category_name (str): The name of the category for which the analysis was performed. Each analysis was performed for a certain subset of
                the attributions, in most cases this subset will be defined by the label of dataset samples of the attributions. So the category name
                is the umbrella term for all the attributions that comprise the analysis, which will, in most cases, be the name of the label.
            clustering_name (str): On top of the embedding a clustering is performed. This clustering name is the name of the clustering that is to be
                retrieved (because usually the analysis contains multiple different clusterings, which are most likely k-means with different k's).
            embedding_name (str): The name of the embedding that is to be retrieved. This is the name of the method that was used to create the
                embedding. Most likely this will be "spectral" for spectral embeddings and "tsne" for a T-SNE embedding.

        Raises:
            ValueError: If the analysis database has already been closed, then a ValueError is raised.
            LookupError: When the analysis for the specified category name, clustering name, and embedding name could not be found, then a LookupError
                is raised.

        Returns:
            Analysis: Returns the analysis for the specified name.
        """

        # Checks if the analysis database has already been closed, if so, a ValueError is raised
        if self.is_closed or self.analysis_file is None:
            raise ValueError('The analysis database has already been closed.')

        # Checks if the specified analysis exists, if not, then an LookupError is raised
        if not self.has_analysis(category_name, clustering_name, embedding_name):
            raise LookupError(
                f'No analysis for category "{category_name}", clustering "{clustering_name}", and embedding '
                '"{embedding_name}" could be found.'
            )

        # Gets the analysis for the specified name, cluster, and embedding
        analysis = self.analysis_file[category_name]
        clustering = analysis['cluster'][clustering_name][()]
        embedding = analysis['embedding'][embedding_name][()]
        attribution_indices = analysis['index'][()]
        eigenvalues = None
        if 'eigenvalue' in self.analysis_file[category_name]['embedding'][embedding_name].attrs.keys():
            eigenvalues = self.analysis_file[category_name]['embedding'][embedding_name].attrs['eigenvalue']

        # Wraps the information of the analysis in an object and returns it
        try:
            human_readable_category_name = self.label_map.get_label_names(category_name)
        except LookupError:
            human_readable_category_name = ''
        return Analysis(
            category_name,
            human_readable_category_name,
            clustering_name,
            clustering,
            embedding_name,
            embedding,
            attribution_indices,
            eigenvalues
        )

    def close(self) -> None:
        """Closes the analysis database."""

        if not self.is_closed:
            self.analysis_file.close()
            self.analysis_file = None
            self.is_closed = True

    def __del__(self) -> None:
        """Destructs the analysis database."""

        self.close()


class AnalysisCategory:
    """Represents a single category in an analysis. One category can contain many analyses for different attributions. The category name is usually an
    umbrella term for all the attributions contained in the analysis. This is most-likely a class name.
    """

    def __init__(self, name: str, human_readable_name: str) -> None:
        """Initializes a new AnalysisCategory instance.

        Args:
            name (str): The name of the category, e.g. a label index or WordNet ID.
            human_readable_name (str): A human-readable version of the category name, e.g. the label name.
        """

        self.name: str = name
        self.human_readable_name: str = human_readable_name


class Analysis:
    """Represents an analysis of multiple attributions."""

    def __init__(
        self,
        category_name: str,
        human_readable_category_name: str,
        clustering_name: str,
        clustering: NDArray[numpy.int64],
        embedding_name: str,
        embedding: NDArray[numpy.float64],
        attribution_indices: NDArray[numpy.int64],
        eigenvalues: NDArray[numpy.float64] | None = None
    ) -> None:
        """Initializes a new Analysis instance.

        Args:
            category_name (str): The name of the category for which the analysis was performed. Each analysis was performed for a certain subset of
                the attributions, in most cases this subset will be defined by the label of dataset samples of the attributions. So the category name
                is the umbrella term for all the attributions that comprise the analysis, which will, in most cases, be the name of the label.
            human_readable_category_name (str): A human readable version of the category name (since category names are usually labels, this can be
                the human-readable name of the label, if the category name is not a label, then the human-readable name should be set to the category
                name itself).
            clustering_name (str): On top of the embedding a clustering is performed. This clustering name is the name of the clustering that is to be
                retrieved (because usually the analysis contains multiple different clusterings, which are most likely k-means with different k's).
            clustering (NDArray[numpy.int64]): The clustering, which is an array that contains for each attribution, that is part of the analysis,
                the number of the cluster to which is belongs.
            embedding_name (str): The name of the embedding that is to be retrieved. This is the name of the method that was used to create the
                embedding. Most likely this will be "spectral" for spectral embeddings and "tsne" for a T-SNE embedding.
            embedding (NDArray[numpy.float64]): The embedding, which contains the embedding vector for all the attributions, that are part of the
                analysis.
            attribution_indices (NDArray[numpy.int64]): Contains a list of the indices of the attributions that correspond to the embeddings and
                cluster points.
            eigenvalues (NDArray[numpy.float64] | None): The eigen values of the embedding. The eigen values must only be specified for normal
                embeddings that are not based on another embedding (see the description for the base_embedding_name parameter for more information).
                Defaults to None.
        """

        self.category_name: str = category_name
        self.human_readable_category_name: str = human_readable_category_name
        self.clustering_name: str = clustering_name
        self.clustering: NDArray[numpy.int64] = clustering
        self.embedding_name: str = embedding_name
        self.embedding: NDArray[numpy.float64] = embedding
        self.attribution_indices: NDArray[numpy.int64] = attribution_indices
        self.eigenvalues: NDArray[numpy.float64] | None = eigenvalues


class Hdf5Dataset:
    """Represents a dataset that is stored in an HDF5 database."""

    def __init__(self, name: str, path: str, label_map: 'LabelMap') -> None:
        """Initializes a new Hdf5Dataset instance.

        Args:
            name (str): The human-readable name of the dataset.
            path (str): The path to the HDF5 file that contains the dataset.
            label_map (LabelMap): The label map, which contains a mapping between the index of the labels and their human-readable names.
        """

        # Stores the arguments for later reference
        self.name: str = name
        self.path: str = path
        self.label_map: LabelMap = label_map

        # Loads the dataset file; the HDF5 dataset is initialized as being closed and the is_closed flag is only set to False after the file has been
        # successfully loaded; this is done to prevent an exception from occurring in the destructor if in an exception is raised during the loading
        # of the file (the destructor would check if the file is closed and try to close it, but since the exception occurs before the dataset_file
        # property is assigned, an AttributeError would be raised; if we were to initialize the dataset_file property with None, we would have to
        # check for None everywhere to satisfy the type checker, which is not very elegant)
        self.is_closed: bool = True
        self.dataset_file: h5py.File = h5py.File(self.path, 'r')
        self.is_closed = False

        # Determines if the dataset allows multiple labels or only single labels (when the dataset is multi-label, then the labels are stored as a
        # boolean NumPy array where the index is the label index and the value determines whether the sample has the label, when the dataset is
        # single-label, then the label is just a scalar value containing the index of the label)
        self.is_multi_label: bool = False
        labels: h5py.Group | h5py.Dataset = self.dataset_file['label']
        if isinstance(labels, h5py.Dataset):
            self.is_multi_label = labels.dtype == numpy.bool
        if isinstance(labels, h5py.Group):
            self.is_multi_label = labels[list(labels.keys())[0]].dtype == numpy.bool

    def get_sample(self, index: int) -> 'Sample':
        """Gets the sample at the specified index.

        Args:
            index (int): The index or key of the sample that is to be retrieved.

        Raises:
            ValueError: When the dataset has already been closed, then a ValueError is raised.
            LookupError: When the specified index is out of range, a LookupError is raised.

        Returns:
            Sample: Returns the sample at the specified index.
        """

        # Checks if the dataset is already closed
        if self.is_closed:
            raise ValueError('The dataset has already been closed.')

        # Extracts the information about the sample from the dataset
        try:
            data = self.dataset_file['data']
            if isinstance(data, h5py.Dataset):
                sample_data = data[index]
            else:
                sample_data = data[list(data.keys())[index]]

            labels = self.dataset_file['label']
            if isinstance(labels, h5py.Dataset):
                sample_label_reference = labels[index]
            else:
                sample_label_reference = labels[list(labels.keys())[index]]
            sample_labels = self.label_map.get_labels(sample_label_reference)
        except IndexError as error:
            raise LookupError(f'No sample with the index {index} could be found.') from error

        # Wraps the sample in an object and returns it
        return Sample(index, sample_data, sample_labels)

    def __getitem__(self, key: int | slice | range | list[int] | tuple[int, ...] | NDArray[numpy.int64]) -> 'Sample | list[Sample]':
        """Gets the specified sample(s). This implements the Python interface for the []-indexer.

        Args:
            key (int | slice | range | list[int] | tuple[int, ...] | NDArray[numpy.int64]): The key of the sample/samples that are to be retrieved.

        Returns:
            Sample | list[Sample]: Returns the sample at the specified index.
        """

        # Checks if the key is a slice, in that case it is converted to a range
        if isinstance(key, slice):
            key = range(*key.indices(len(self)))

        # Checks if the key contains multiple indices, in that case all samples for the specified list of indices are retrieved
        if isinstance(key, (range, list, tuple, numpy.ndarray)):
            return [self.get_sample(index) for index in key]

        # If the key is just a single index, the sample is directly retrieved
        return self.get_sample(key)

    def __len__(self) -> int:
        """Retrieves the number of samples in the dataset. This implements the Python interface for the len() built-in.

        Returns:
            int: Returns the number of samples in the datasets.
        """

        return len(self.dataset_file['data'])

    def close(self) -> None:
        """Closes the dataset."""

        if not self.is_closed:
            self.dataset_file.close()
            self.is_closed = True

    def __del__(self) -> None:
        """Destructs the dataset."""

        self.close()


class ImageDirectoryDataset:
    """Represents an image dataset, where the image files are in a directory hierarchy were the names of the directories
    represent the labels of the images.
    """

    def __init__(
        self,
        name: str,
        path: str,
        label_index_regex: str | None,
        label_word_net_id_regex: str | None,
        input_width: int,
        input_height: int,
        down_sampling_method: DownSamplingMethod,
        up_sampling_method: UpSamplingMethod,
        label_map: 'LabelMap'
    ) -> None:
        """Initializes a new ImageDirectoryDataset instance.

        Args:
            name (str): The human-readable name of the dataset.
            path (str): The path to the directory that contains the directories for the labels, which in turn contain the images that belong to the
                respective label.
            label_index_regex (str | None): A regular expression, which is used to parse the path of a sample for the label index. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or label_word_net_id_regex must be specified.
            label_word_net_id_regex (str | None): A regular expression, which is used to parse the path of a sample for the WordNet ID. The sample
                index must be captured in the first group. Can be None, but either label_index_regex or label_word_net_id_regex must be specified.
            input_width (int): The width of the input to the model. This is used to resize the dataset samples to the same size as the model expects
                its inputs to be.
            input_height (int): The height of the input to the model. This is used to resize the dataset samples to the same size as the model expects
                its inputs to be.
            down_sampling_method (DownSamplingMethod): The method that is to be used to down-sample images from the dataset that are larger than the
                input to the model.
            up_sampling_method (UpSamplingMethod): The method that is to be used to up-sample images from the dataset that are smaller than the input
                to the model.
            label_map (LabelMap): The label map, which contains a mapping between the index of the labels and their human-readable names.

        Raises:
            ValueError: If neither the label index RegEx nor the label WordNet ID RegEx was specified, a ValueError is raised. If both the label index
                RegEx and the label WordNet ID RegEx were specified, a ValueError is raised. If the specified up-sampling method is not supported, a
                ValueError is raised. If the specified down-sampling method is not supported, a ValueError is raised.
        """

        # Initializes some class members
        self.is_closed: bool = False

        # Validates the arguments
        if label_index_regex is None and label_word_net_id_regex is None:
            raise ValueError('Either the label index RegEx or the label WordNet ID RegEx must be specified.')
        if label_index_regex is not None and label_word_net_id_regex is not None:
            raise ValueError('Only the label index RegEx or the label WordNet ID RegEx must be specified, not both.')
        if down_sampling_method not in ['none', 'center_crop', 'resize']:
            raise ValueError(f'The down-sampling method "{down_sampling_method}" is not supported.')
        up_sampling_methods = ['none', 'fill_zeros', 'fill_ones', 'edge_repeat', 'mirror_edge', 'wrap_around', 'resize']
        if up_sampling_method not in up_sampling_methods:
            raise ValueError(f'The up-sampling method "{up_sampling_method}" is not supported.')

        # Stores the arguments for later reference
        self.name: str = name
        self.path: str = path
        self.label_index_regex: str | None = label_index_regex
        self.label_word_net_id_regex: str | None = label_word_net_id_regex
        self.input_width: int = input_width
        self.input_height: int = input_height
        self.down_sampling_method: DownSamplingMethod = down_sampling_method
        self.up_sampling_method: UpSamplingMethod = up_sampling_method
        self.label_map: LabelMap = label_map

        # Loads a list of all the paths to all samples in the dataset (they are sorted, because the index of the sorted paths corresponds to the
        # sample index that has to be specified in the get_sample method)
        self.sample_paths: list[str]
        if os.path.exists(self.path + '_paths.txt'):
            with open(self.path + '_paths.txt', encoding='utf-8') as f:
                self.sample_paths = sorted(
                    [os.path.join(os.path.dirname(self.path), path) for path in f.read().split('\n')]
                )
        else:
            self.sample_paths = sorted(glob.glob(os.path.join(self.path, '**/*.*'), recursive=True))
        assert len(self.sample_paths) > 0, 'No Images found.'

    def get_sample(self, index: int) -> 'Sample':
        """Gets the sample at the specified index.

        Args:
            index (int): The index of the sample that is to be retrieved.

        Raises:
            ValueError: If the dataset has already been closed, then a ValueError is raised.
            LookupError: When the specified index is out of range, a LookupError is raised. If the label for the retrieved sample could not be
                determined from the label lookup, then a LookupError: is raised

        Returns:
            Sample: Returns the sample at the specified index.
        """

        # Checks if the dataset is already closed
        if self.is_closed:
            raise ValueError('The dataset has already been closed.')

        # Gets the path to the sample file
        if index >= len(self.sample_paths):
            raise LookupError(f'No sample with the index {index} could be found.')
        sample_path = self.sample_paths[index]

        # Determines the label of the sample by parsing the path
        label: Label | None = None
        if self.label_index_regex is not None:
            match = re.match(self.label_index_regex, sample_path)
            if match:
                label = self.label_map.get_label_from_index(int(match.groups()[0]))
        if self.label_word_net_id_regex is not None:
            match = re.match(self.label_word_net_id_regex, sample_path)
            if match:
                label = self.label_map.get_label_from_word_net_id(match.groups()[0])
        if label is None:
            raise LookupError('The label for the sample could not be determined based on the label map.')

        # Loads the image from file and converts to a NumPy array
        image = Image.open(sample_path).convert('RGB')
        image_array = numpy.array(image)

        # Performs the re-sampling of the image (depending on whether it is smaller or larger than the target input size, different methods are used,
        # which are specified in the project file)
        image_array = self.re_sample_image(image_array)

        # Returns the sample
        return Sample(index, image_array, label)

    def re_sample_image(self, image: NDArray[numpy.float64]) -> NDArray[numpy.float64]:
        """Re-samples an image based on the specified up-sampling and down-sampling methods.

        Args:
            image (NDArray[numpy.float64]): The image that is to be re-sampled.

        Returns:
            NDArray[numpy.float64]: Returns the re-sampled image.
        """

        # If at least one of the image dimensions is smaller than the target size, then the image is first up-sampled (if for example the width is
        # smaller than the target width but the height is larger, then the image is first up-sampled so that the width matched the target width, in
        # the next step, the image will be down-sampled, so that the height also matches the target width)
        width = image.shape[0]
        height = image.shape[1]
        if width < self.input_width or height < self.input_height:
            if self.up_sampling_method == 'fill_zeros':
                image = add_border(image, max(width, self.input_width), max(height, self.input_height), 'fill_zeros')
            elif self.up_sampling_method == 'fill_ones':
                image = add_border(image, max(width, self.input_width), max(height, self.input_height), 'fill_ones')
            elif self.up_sampling_method == 'edge_repeat':
                image = add_border(image, max(width, self.input_width), max(height, self.input_height), 'edge_repeat')
            elif self.up_sampling_method == 'mirror_edge':
                image = add_border(image, max(width, self.input_width), max(height, self.input_height), 'mirror_edge')
            elif self.up_sampling_method == 'wrap_around':
                image = add_border(image, max(width, self.input_width), max(height, self.input_height), 'wrap_around')
            elif self.up_sampling_method == 'resize':
                image = numpy.array(Image.fromarray(image).resize((self.input_width, self.input_height)))

        # If at least one of the image dimensions is greater than the target size, then the image is down-sampled
        if width > self.input_width or height > self.input_height:
            if self.down_sampling_method == 'center_crop':
                image = center_crop(image, self.input_width, self.input_height)
            elif self.down_sampling_method == 'resize':
                image = numpy.array(Image.fromarray(image).resize((self.input_width, self.input_height)))

        # Returns the re-sampled image
        return image

    def __getitem__(self, key: int | slice | range | list[int] | tuple[int, ...] | NDArray[numpy.int64]) -> 'Sample | list[Sample]':
        """Gets the specified sample(s). This implements the Python interface for the []-indexer.

        Args:
            key (int | slice | range | list[int] | tuple[int, ...] | NDArray[numpy.int64]): The key of the sample/samples that are to be retrieved.

        Returns:
            Sample | list[Sample]: Returns the sample at the specified index.
        """

        # Checks if the key is a slice, in that case it is converted to a range
        if isinstance(key, slice):
            key = range(*key.indices(len(self)))

        # Checks if the key contains multiple indices, in that case all samples for the specified list of indices are retrieved
        if isinstance(key, (range, list, tuple, numpy.ndarray)):
            return [self.get_sample(index) for index in key]

        # If the key is just a single index, the sample is directly retrieved
        return self.get_sample(key)

    def __len__(self) -> int:
        """Retrieves the number of samples in the dataset. This implements the Python interface for the len() built-in.

        Returns:
            int: Returns the number of samples in the datasets.
        """

        return len(self.sample_paths)

    def close(self) -> None:
        """Closes the dataset."""

        self.is_closed = True

    def __del__(self) -> None:
        """Destructs the dataset."""

        self.close()


class Sample:
    """Represents a sample in a dataset."""

    def __init__(self, index: int, data: NDArray[numpy.float64], labels: 'Label | list[Label]') -> None:
        """Initializes a new Sample instance.

        Args:
            index (int): The index of the sample within the dataset.
            data (NDArray[numpy.float64]): The data that represents the sample.
            labels (Label | list[Label]): The label or a list of all the labels that the sample has.
        """

        # Stores the arguments for later use
        self.index: int = index
        self.data: NDArray[numpy.float64] = data
        if not isinstance(labels, list):
            labels = [labels]
        self.labels: list[Label] = labels

        # Images may come from different sources, e.g. in PyTorch the ordering of the axes is Channels x Width x Height, while in other sources, the
        # ordering is Width x Height x Channel, this code tries to guess which axis represents the RGB channels, and puts them in the order Width x
        # Height x Channel
        if numpy.argmin(self.data.shape) == 0:
            self.data = numpy.moveaxis(self.data, [0, 1, 2], [2, 0, 1])

        # The pixel values of the image may be in three different value ranges: [-1.0, 1.0], [0.0, 1.0], and [0, 255], this code tries to find out
        # which it is and de-normalizes it to the value range of [0, 255], unfortunately, it is not guaranteed that the actual value range of the
        # images has exactly these bounds, because not all images contain pure black or pure white pixels, therefore, a heuristic is used, where the
        # L1 distance between the actual pixel value range and the three value ranges is computed
        if self.data.dtype != numpy.uint8:
            actual_pixel_value_range = numpy.array([numpy.min(self.data), numpy.max(self.data)])
            distances = numpy.array([[-1.0, 1.0], [0.0, 1.0], [0.0, 255.0]]) - actual_pixel_value_range
            distances = numpy.abs(numpy.sum(distances, axis=1))
            detected_pixel_value_range_index = numpy.argmin(distances)
            if detected_pixel_value_range_index == 0:
                self.data += 1
                self.data *= 255.0 / 2.0
            elif detected_pixel_value_range_index == 1:
                self.data *= 255.0
            self.data = self.data.astype(numpy.uint8)


class LabelMap:
    """Represents a map between output neuron indices and their respective human-readable label name."""

    def __init__(self, path: str) -> None:
        """Initializes a new LabelMap instance.

        Args:
            path (str): The path to the label map JSON file.
        """

        # Stores the path to the label map JSON file for later reference
        self.path: str = path

        # Loads the label map from the specified JSON file
        self.labels: list[Label] = []
        with open(self.path, 'r', encoding='utf-8') as label_map_file:
            labels: list[LabelJson] = json.load(label_map_file)
            for label in labels:
                self.labels.append(Label(label['index'], label['word_net_id'], label['name']))

    @overload
    def get_labels(self, reference: int | str | numpy.int64) -> 'Label':
        """Retrieves the human-readable name of the label that matches the specified reference. The reference may either be an index or a WordNet ID.

        Args:
            reference (int | str | numpy.int64): The reference for which the matching label is to be retrieved. This can either be an index or a
                WordNet ID.

        Returns:
            Label: Returns the human-readable name of the label that matched the specified reference.
        """

    @overload
    def get_labels(self, reference: list[int] | tuple[int, ...] | NDArray[numpy.int64]) -> list['Label']:
        """Retrieves the human-readable names of the labels that match the specified reference. The reference must be a n-hot encoded vector.

        Args:
            reference (list[int] | tuple[int, ...] | NDArray[numpy.int64]): The reference for which all matching labels are to be retrieved. This must
                be a n-hot encoded vector.

        Returns:
            list[Label]: Returns a list of all the human-readable names of the labels that matched the specified reference.
        """

    @overload
    def get_labels(self, reference: h5py.Dataset) -> 'Label | list[Label]':
        """Retrieves the human-readable names of the labels that match the specified reference. The reference must be a n-hot encoded vector.

        Args:
            reference (h5py.Dataset): The reference for which all matching labels are to be retrieved. This must be a n-hot encoded vector.

        Returns:
            Label | list[Label]: Returns a list of all the human-readable names of the labels that matched the specified reference.
        """

    def get_labels(
        self,
        reference: int | str | numpy.int64 | list[int] | tuple[int, ...] | NDArray[numpy.int64] | h5py.Dataset
    ) -> 'Label | list[Label]':
        """Retrieves the labels that match the specified reference. The reference may either be an index, a n-hot encoded vector, or a WordNet ID.

        Args:
            reference (int | str | numpy.int64 | list[int] | tuple[int, ...] | NDArray[numpy.int64] | h5py.Dataset): The reference for which all
                matching labels are to be retrieved. This can either be an index, a n-hot encoded vector, or a WordNet ID.

        Raises:
            LookupError: When no labels for the specified reference could be found (or one or more in case of a n-hot vector), then a LookupError is
                raised.

        Returns:
            Label | list[Label]: Returns the label or a list of all labels that matched the specified reference.
        """

        if isinstance(reference, int):
            return self.get_label_from_index(reference)
        if isinstance(reference, numpy.integer):
            return self.get_label_from_index(reference.item())
        if isinstance(reference, str):
            return self.get_label_from_word_net_id(reference)
        if isinstance(reference, (list, tuple)):
            return [self.get_label_from_index(index) for index in reference]
        if isinstance(reference, numpy.ndarray):
            return self.get_labels_from_n_hot_vector(reference)
        if isinstance(reference, h5py.Dataset) and len(reference.shape) == 0 and reference.dtype == numpy.uint16:
            return self.get_label_from_index(reference[()])
        if isinstance(reference, h5py.Dataset) and reference.dtype == numpy.bool:
            return self.get_labels_from_n_hot_vector(reference[:])
        raise LookupError(f'No labels for the specified reference "{reference}" could be found.')

    @overload
    def get_label_names(self, reference: int | str | numpy.int64) -> str:
        """Retrieves the human-readable name of the label that matches the specified reference. The reference may either be an index or a WordNet ID.

        Args:
            reference (int | str | numpy.int64): The reference for which the matching label is to be retrieved. This can either be an index or a
                WordNet ID.

        Returns:
            str: Returns the human-readable name of the label that matched the specified reference.
        """

    @overload
    def get_label_names(self, reference: list[int] | tuple[int, ...] | NDArray[numpy.int64]) -> list[str]:
        """Retrieves the human-readable names of the labels that match the specified reference. The reference must be a n-hot encoded vector.

        Args:
            reference (list[int] | tuple[int, ...] | NDArray[numpy.int64]): The reference for which all matching labels are to be retrieved. This must
                be a n-hot encoded vector.

        Returns:
            list[str]: Returns a list of all the human-readable names of the labels that matched the specified reference.
        """

    @overload
    def get_label_names(self, reference: h5py.Dataset) -> str | list[str]:
        """Retrieves the human-readable names of the labels that match the specified reference. The reference must be a n-hot encoded vector.

        Args:
            reference (h5py.Dataset): The reference for which all matching labels are to be retrieved. This must be a n-hot encoded vector.

        Returns:
            str | list[str]: Returns a list of all the human-readable names of the labels that matched the specified reference.
        """

    def get_label_names(
        self,
        reference: int | str | numpy.int64 | list[int] | tuple[int, ...] | NDArray[numpy.int64] | h5py.Dataset
    ) -> str | list[str]:
        """Retrieves the human-readable names of the labels that match the specified reference. The reference may either be an index, a n-hot encoded
        vector, or a WordNet ID, the method will figure out which it is and retrieve the correct labels.

        Args:
            reference (int | str | numpy.int64 | list[int] | tuple[int, ...] | NDArray[numpy.int64] | h5py.Dataset): The reference for which all
                matching labels are to be retrieved. This can either be an index, a n-hot encoded vector, or a WordNet ID.

        Raises:
            LookupError: When no labels for the specified reference could be found (or one or more in case of a n-hot vector), then a LookupError is
                raised.

        Returns:
            str | list[str]: Returns the human-readable name or a list of all the human-readable names of the labels that matched the specified
                reference.
        """

        if isinstance(reference, int):
            return self.get_label_name_from_index(reference)
        if isinstance(reference, numpy.integer):
            return self.get_label_name_from_index(reference.item())
        if isinstance(reference, str):
            return self.get_label_name_from_word_net_id(reference)
        if isinstance(reference, (list, tuple)):
            return [self.get_label_name_from_index(index) for index in reference]
        if isinstance(reference, numpy.ndarray):
            return self.get_label_names_from_n_hot_vector(reference)
        if isinstance(reference, h5py.Dataset) and len(reference.shape) == 0 and reference.dtype == numpy.uint16:
            return self.get_label_name_from_index(reference[()])
        if isinstance(reference, h5py.Dataset) and reference.dtype == numpy.bool:
            return self.get_label_names_from_n_hot_vector(reference[:])
        raise LookupError(f'No labels for the specified reference "{reference}" could be found.')

    def get_label_from_index(self, index: int) -> 'Label':
        """Retrieves the label with the specified index.

        Args:
            index (int): The index of the label.

        Raises:
            LookupError: If the specified index does not exist, then a LookupError is raised.

        Returns:
            Label: Returns the label.
        """

        for label in self.labels:
            if label.index == index:
                return label
        raise LookupError(f'No label with the specified index {index} could be found.')

    def get_label_name_from_index(self, index: int) -> str:
        """Retrieves the human-readable name of the label with the specified index.

        Args:
            index (int): The index of the label.

        Returns:
            str: Returns the human-readable name of the label.
        """

        return self.get_label_from_index(index).name

    def get_labels_from_n_hot_vector(self, n_hot_vector: NDArray[numpy.int64 | numpy.bool]) -> list['Label']:
        """Retrieves the labels that are specified by the n-hot encoded vector.

        Args:
            n_hot_vector (NDArray[numpy.int64 | numpy.bool]): A n-hot encoded vector, where the indices are the label indices and the values are
                True/1 when the label is present and False/0 when the label is not present.

        Raises:
            LookupError: If the length of the n-hot encoded vector is greater than the number of labels (that is there are indices for which there are
                no labels), then a LookupError is raised.

        Returns:
            list[Label]: Returns a list of all the labels that are specified by the n-hot encoded vector.
        """

        try:
            labels: list[Label] = []
            for index in numpy.argwhere(n_hot_vector):
                labels.append(self.get_label_from_index(index[0]))
            return labels
        except LookupError as lookup_error:
            raise LookupError('One or more labels for the n-hot encoded vector do not exist.') from lookup_error

    def get_label_names_from_n_hot_vector(self, n_hot_vector: NDArray[numpy.int64]) -> list[str]:
        """Retrieves the human-readable names of the labels that are specified by the n-hot encoded vector.

        Args:
            n_hot_vector (NDArray[numpy.int64]): A n-hot encoded vector, where the indices are the label indices and the values are True/1 when the
                label is present and False/0 when the label is not present.

        Returns:
            list[str]: Returns a list of all the labels that are specified by the n-hot encoded vector.
        """

        return [label.name for label in self.get_labels_from_n_hot_vector(n_hot_vector)]

    def get_label_from_word_net_id(self, word_net_id: str) -> 'Label':
        """Retrieves the label with the specified WordNet ID.

        Args:
            word_net_id (str): The WordNet ID of the label.

        Raises:
            LookupError: If the specified WordNet ID does not exist, then a LookupError is raised.

        Returns:
            Label: Returns the label.
        """

        for label in self.labels:
            if label.word_net_id == word_net_id:
                return label
        raise LookupError(f'No label with the specified WordNet ID "{word_net_id}" could be found.')

    def get_label_name_from_word_net_id(self, word_net_id: str) -> str:
        """Retrieves the human-readable name of the label with the specified WordNet ID.

        Args:
            word_net_id (str): The WordNet ID of the label.

        Returns:
            str: Returns the human-readable name of the label.
        """

        return self.get_label_from_word_net_id(word_net_id).name


@dataclass
class Label:
    """Represents a label of the dataset."""

    index: int
    """The index of the output neuron that corresponds to the label."""

    word_net_id: str
    """The WordNet ID of the synset that describes the label (this is only necessary for some datasets like ImageNet)."""

    name: str
    """The human-readable name of the label."""


class Workspace:
    """Represents a workspace, which may consist of multiple projects."""

    def __init__(self) -> None:
        """Initializes a new Workspace instance."""

        self.is_closed: bool = False
        self.projects: list[Project] = []

    def add_project(self, path: str) -> None:
        """Adds a new project to the workspace.

        Args:
            path (str): The path to the project YAML file.

        Raises:
            ValueError: If the workspace is already closed, a ValueError is raised.
        """

        if self.is_closed:
            raise ValueError('The workspace has already been closed.')

        self.projects.append(Project(path))

    def get_project_names(self) -> list[str]:
        """Retrieves the names of all the loaded projects.

        Raises:
            ValueError: If the workspace is already closed, a ValueError is raised.

        Returns:
            list[str]: Returns a list of the names of all loaded projects.
        """

        if self.is_closed:
            raise ValueError('The workspace has already been closed.')

        project_names = []
        for project in self.projects:
            project_names.append(project.name)
        return project_names

    def get_project(self, name: str) -> 'Project':
        """Retrieves the project with the specified name

        Args:
            name (str): The name of the project that is to be retrieved.

        Raises:
            ValueError: If the workspace is already closed, a ValueError is raised.
            LookupError: If the project with the specified name could not be found, then a LookupError is raised.

        Returns:
            Project: Returns the project with the specified name.
        """

        # If the workspace is closed, then a ValueError is raised
        if self.is_closed:
            raise ValueError('The workspace has already been closed.')

        # Searches for the project with the specified name and returns it if it was found
        for project in self.projects:
            if project.name == name:
                return project

        # If no project with the specified name could not be found, then an exception is raised
        raise LookupError(f'The project with the name "{name}" could not be found.')

    def close(self) -> None:
        """Closes the workspace and all projects within it."""

        if not self.is_closed:
            for project in self.projects:
                project.close()
            self.projects = []
            self.is_closed = True

    def __del__(self) -> None:
        """Destructs the workspace."""

        self.close()


class ProjectFileYaml(TypedDict):
    """Represents the project YAML file, which contains the definition of the project."""

    project: 'ProjectYaml'
    """The project definition that is contained in the project YAML file."""


class ProjectYaml(TypedDict):
    """Represents a project definition, which is contained in project YAML file."""

    name: str
    """The name of the project."""

    model: str
    """The name of the model that is used in the project and which was used to produce the attributions."""

    label_map: str
    """The path to the file that contains the label map."""

    dataset: 'DatasetYaml'
    """The dataset that was used to produce the attributions."""

    attributions: 'AttributionYaml'
    """The attribution definitions that contain the attributions for the samples of the datasets."""

    analyses: list['AnalysisYaml']
    """A list of analysis definitions that contain the analyses of the attributions."""


class DatasetYaml(TypedDict):
    """Represents a dataset definition, which is contained in the project definition of the project YAML file."""

    name: str
    """The name of the dataset."""

    type: DatasetType
    """The type of the dataset, which can be either HDF5 or image directory."""

    path: str
    """The path to the dataset file or directory."""

    input_width: int
    """The width of the inputs to the model. The images in the dataset are sampled up or down to this size using the specified up and down sampling
    methods.
    """

    input_height: int
    """The height of the inputs to the model. The images in the dataset are sampled up or down to this size using the specified up and down sampling
    methods.
    """

    up_sampling_method: UpSamplingMethod
    """The method that is used to up-sample images from the dataset that are smaller than the input to the model."""

    down_sampling_method: DownSamplingMethod
    """The method that is used to down-sample images from the dataset that are larger than the input to the model."""

    label_index_regex: str | None
    """A regular expression, which is used to parse the path of a sample for the label index. The sample index must be captured in the first group.
    Can be None, but if the dataset type is "image_directory", then either "label_index_regex" or "label_word_net_id_regex" must be specified.
    """

    label_word_net_id_regex: str | None
    """A regular expression, which is used to parse the path of a sample for the WordNet ID. The sample index must be captured in the first group. Can
    be None, but if the dataset type is "image_directory", then either "label_index_regex" or "label_word_net_id_regex" must be specified.
    """


class AttributionYaml(TypedDict):
    """Represents an attribution definition, which is contained in the project definition of the project YAML file."""

    attribution_method: str
    """The name of the method that was used to compute the attributions, e.g., the name of the LRP variant."""

    attribution_strategy: AttributionStrategy
    """The strategy that was used to compute the attributions, which can be either the "true_label", which means that the relevance of the true label
    are propagated back to get an attribution that shows the evidence for and against the true label, or the predicted label, which means that the
    relevance of the predicted label are propagated back to get an attribution that shows the evidence for and against the predicted label."""

    sources: list[str]
    """A list of paths to attribution database files."""


class AnalysisYaml(TypedDict):
    """Represents an analysis definition, which is contained in the project definition of the project YAML file."""

    analysis_method: str
    """The name of the method that was used to compute the analysis, e.g., "Spectral"."""

    sources: list[str]
    """A list of paths to analysis database files."""


class LabelJson(TypedDict):
    """Represents a label in the label map JSON file."""

    index: int
    """The index of the label."""

    word_net_id: str
    """The WordNet ID of the label."""

    name: str
    """The human-readable name of the label."""
