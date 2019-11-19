"""Contains the data model abstraction."""
# pylint: disable=too-many-lines

import os
import re
import json
import glob

import yaml
import h5py
import numpy
from PIL import Image

from .image_processing import add_border, center_crop, render_heatmap, render_superimposed_heatmap


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
        self.analyses = {}

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
                            project['dataset']['input_width'],
                            project['dataset']['input_height'],
                            project['dataset']['down_sampling_method'],
                            project['dataset']['up_sampling_method'],
                            self.label_map
                        )
                    else:
                        raise ValueError('The specified dataset type "{0}" is unknown.'.format(dataset_type))

                # Loads the attributions of the project
                if project['attributions'] is not None:
                    self.attribution_method = project['attributions']['attribution_method']
                    self.attribution_strategy = project['attributions']['attribution_strategy']
                    for attribution_database in project['attributions']['sources']:
                        self.attributions.append(AttributionDatabase(
                            os.path.join(working_directory, attribution_database),
                            self.label_map
                        ))

                # Loads the analyses of the project
                if project['analyses'] is not None:
                    for analysis in project['analyses']:
                        analysis_method = analysis['analysis_method']
                        if analysis_method not in self.analyses:
                            self.analyses[analysis_method] = []
                        for analysis_database in analysis['sources']:
                            self.analyses[analysis_method].append(AnalysisDatabase(
                                os.path.join(working_directory, analysis_database),
                                self.label_map
                            ))
            except yaml.YAMLError:
                raise ValueError('An error occurred while loading the project file.')

    def get_sample(self, index):
        """
        Retrieves the sample from the dataset with the specified index.

        Parameters
        ----------
            index: int
                The index of the dataset sample.

        Raises
        ------
            LookupError
                If no dataset sample with the specified index could be found, then a LookupError is raised.

        Returns
        -------
            Sample
                Returns the dataset sample with the specified index.
        """

        return self.dataset.get_sample(index)

    def get_attribution(self, index):
        """
        Retrieves the attribution for the specified index.

        Parameters
        ----------
            index: int
                The index of the attribution.

        Raises
        ------
            LookupError
                If no attribution with the specified index could be found, then a LookupError is raised

        Returns
        -------
            Attribution
                Returns the attribution with the specified index.
        """

        for attribution_database in self.attributions:
            if attribution_database.has_attribution(index):
                return attribution_database.get_attribution(index)

        raise LookupError('No attribution with the specified index {0} could be found.'.format(index))

    def get_analysis_methods(self):
        """
        Retrieves the names of all the analysis methods that are in this project.

        Returns
        -------
            list of str
                Returns a list of the names of the all the analysis methods in this project.
        """

        return list(self.analyses.keys())

    def get_analysis_categories(self, analysis_method):
        """
        Retrieves the names of the categories that are in the analyses of the specified analysis method.

        Parameter
        ---------
            analysis_method: str
                The name of the analysis method for which the categories are to be retrieved.

        Raises
        ------
            LookupError
                If the specified analysis method does not exist, then a LookupError is raised.

        Returns
        -------
            list of str
                Returns a list of the names of the categories.
        """

        if analysis_method not in self.analyses:
            raise LookupError('The specified analysis method "{0}" could not be found.'.format(analysis_method))

        categories = []
        for analysis in self.analyses[analysis_method]:
            for category in analysis.get_categories():
                if category.name not in map(lambda c: c.name, categories):
                    categories.append(category)

        return categories

    def get_analysis_clustering_names(self, analysis_method):
        """
        Retrieves the names of the clustering methods that are in the analyses of the specified analysis method.

        Parameter
        ---------
            analysis_method: str
                The name of the analysis method for which the clusterings are to be retrieved.

        Raises
        ------
            LookupError
                If the specified analysis method does not exist, then a LookupError is raised.

        Returns
        -------
            list of str
                Returns a list of the names of the clusterings.
        """

        if analysis_method not in self.analyses:
            raise LookupError('The specified analysis method "{0}" could not be found.'.format(analysis_method))

        return self.analyses[analysis_method][0].get_clustering_names()

    def get_analysis_embedding_names(self, analysis_method):
        """
        Retrieves the names of the embedding methods that are in the analyses of the specified analysis method.

        Parameter
        ---------
            analysis_method: str
                The name of the analysis method for which the embeddings are to be retrieved.

        Raises
        ------
            LookupError
                If the specified analysis method does not exist, then a LookupError is raised.

        Returns
        -------
            list of str
                Returns a list of the names of the embeddings.
        """

        if analysis_method not in self.analyses:
            raise LookupError('The specified analysis method "{0}" could not be found.'.format(analysis_method))

        return self.analyses[analysis_method][0].get_embedding_names()

    def get_analysis(self, analysis_method, category_name, clustering_name, embedding_name):
        """
        Retrieves a complete analysis.

        Parameters
        ----------
            analysis_method: str
                The name of the analysis method from which the analysis is to be retrieved.
            category_name: str
                The name of the category for which the analysis was performed. Each analysis was performed for a certain
                subset of the attributions, in most cases this subset will be defined by the label of dataset samples of
                the attributions. So the category name is the umbrella term for all the attributions that comprise the
                analysis, which will, in most cases, be the name of the label.
            clustering_name: str
                On top of the embedding a clustering is performed. This clustering name is the name of the clustering
                that is to be retrieved (because usually the analysis contains multiple different clusterings, which are
                most likely k-means with different k's).
            embedding_name: str
                The name of the embedding that is to be retrieved. This is the name of the method that was used to
                create the embedding. Most likely this will be "spectral" for spectral embeddings and "tsne" for a
                T-SNE embedding.

        Raises
        ------
            ValueError
                If the analysis database has already been closed, then a ValueError is raised.
            LookupError
                When the analysis for the specified analysis method, category name, clustering name, and embedding name
                could not be found, then a LookupError is raised.

        Returns
        -------
            Analysis
                Returns the analysis for the specified name.
        """

        if analysis_method not in self.analyses:
            raise LookupError('The specified analysis method "{0}" could not be found.'.format(analysis_method))

        for analysis_database in self.analyses[analysis_method]:
            if analysis_database.has_analysis(category_name, clustering_name, embedding_name):
                return analysis_database.get_analysis(category_name, clustering_name, embedding_name)

        raise LookupError(
            'No analysis in the category "{0}" with the clustering "{1}" and embedding "{2}" could be found.'.format(
                category_name,
                clustering_name,
                embedding_name
            )
        )

    def close(self):
        """Closes the project, its dataset, and all of its sources."""

        if not self.is_closed:
            if self.dataset is not None:
                self.dataset.close()
            for attribution in self.attributions:
                attribution.close()
            for analysis_method in self.analyses:
                for analysis in self.analyses[analysis_method]:
                    analysis.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the project."""

        self.close()


class AttributionDatabase:
    """Represents a single attribution database, which contains the attributions for the dataset samples."""

    def __init__(self, attribution_path, label_map):
        """
        Initializes a new AttributionDatabase instance.

        Parameters
        ----------
            attribution_path: str
                The path to the file that contains the attribution database.
            label_map: LabelMap
                The label map, which contains a mapping between the index of the labels and their human-readable names.
        """

        # Initializes some class members
        self.is_closed = False
        self.attribution_file = None

        # Stores the arguments for later reference
        self.attribution_path = attribution_path
        self.label_map = label_map

        # Loads the attribution files
        self.attribution_file = h5py.File(self.attribution_path, 'r')

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

        if 'index' in self.attribution_file.keys():
            return index in self.attribution_file['index']
        return index <= self.attribution_file['attribution'].shape[0]

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
            LookupError
                When the no attribution with the specified index exists, then an LookupError is raised.

        Returns
        -------
            Attribution
                Returns the attribution with the specified index.
        """

        # Checks if the attribution database has already been closed, if so, a ValueError is raised
        if self.is_closed:
            raise ValueError('The attribution database has already been closed.')

        # Checks if the specified attribution exists, if not, then an LookupError is raised
        if not self.has_attribution(index):
            raise LookupError('No attribution with the index {0} could be found.'.format(index))

        # Check where is the searched index in the attribution file
        original_index = index
        if 'index' in self.attribution_file:
            index = numpy.where(index == self.attribution_file['index'][:])
            index = index[0][0].item()

        # Extracts the information about the sample from the dataset
        attribution_data = self.attribution_file['attribution'][index]
        attribution_label_reference = self.attribution_file['label'][index]
        attribution_labels = self.label_map.get_labels(attribution_label_reference)
        attribution_prediction = self.attribution_file['prediction'][index]

        # Wraps the attribution in an object and returns it
        return Attribution(
            original_index,
            attribution_data,
            attribution_labels,
            attribution_prediction
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

    def __init__(self, index, data, labels, prediction):
        """
        Initializes a new Attribution instance.

        Parameters
        ----------
            index: int
                The index of the attribution, which is the index of the sample for which the attribution was created.
            data: numpy.ndarray
                The attribution data, which is a raw heatmap.
            labels: str or list
                The ground truth label or a list of the ground truth labels of the sample for which the attribution was
                created.
            prediction: numpy.ndarray
                The original output of the model.
        """

        # Stores the parameters for later use
        self.index = index
        self.data = data
        if not isinstance(labels, list):
            labels = [labels]
        self.labels = labels
        self.prediction = prediction

        # Heatmaps (the attribution data) may come from different sources, e.g. in PyTorch the ordering of the axes is
        # Channels x Width x Height, while in other sources, the ordering is Width x Height x Channel, this code tries
        # to guess which axis represents the RGB channels, and puts them in the order Width x Height x Channel
        if numpy.argmin(self.data.shape) == 0:
            self.data = numpy.moveaxis(self.data, [0, 1, 2], [2, 0, 1])

    def render_heatmap(self, color_map, superimpose=None):
        """
        Takes the raw attribution data and converts it so that the data can be visualized as a heatmap.

        Parameters
        ----------
            color_map: str
                The name of color map that is to be used to render the heatmap.
            superimpose: numpy.ndarray
                An optional image onto which the heatmap should be superimposed.

        Raises
        ------
            ValueError
                If the specified color map is unknown, then a ValueError is raised.
        """

        if superimpose is not None:
            return render_superimposed_heatmap(self.data, superimpose, color_map)
        else:
            return render_heatmap(self.data, color_map)


class AnalysisDatabase:
    """Represents a single analysis database, which contains the analysis of attributions."""

    def __init__(self, analysis_path, label_map):
        """
        Initializes a new AnalysisDatabase instance.

        Parameters
        ----------
            analysis_path: str
                The path to the file that contains the analysis database.
            label_map: LabelMap
                The label map, which contains a mapping between the index of the labels and their human-readable names.
        """

        # Initializes some class members
        self.is_closed = False
        self.analysis_file = None

        # Stores the arguments for later reference
        self.analysis_path = analysis_path
        self.label_map = label_map

        # Loads the analysis file
        self.analysis_file = h5py.File(self.analysis_path, 'r')

    def get_categories(self):
        """
        Retrieves the names of all the categories that are contained in this analysis database. The category names are
        umbrella terms for the attributions for which the analysis was performed. In most cases this will be the
        name/index/WordNet ID of the label of the dataset samples of the attributions.

        Raises
        ------
            ValueError
                If the analysis database has already been closed, then a ValueError is raised.

        Returns
        -------
            list of AnalysisCategory
                Returns a list containing all the categories that are contained in this analysis database.
        """

        if self.is_closed:
            raise ValueError('The analysis database has already been closed.')

        categories = []
        for category_name in self.analysis_file.keys():
            try:
                human_readable_category_name = self.label_map.get_labels(category_name)
            except LookupError:
                human_readable_category_name = ''
            categories.append(AnalysisCategory(category_name, human_readable_category_name))

        return categories

    def get_clustering_names(self):
        """
        Retrieves the names of all the clusterings that are contained in this analysis database. The clustering names
        are usually the name of the method with which the clustering was generated. Most likely this will be k-means
        with a specific value for k, e.g. 'kmeans-10'.

        Raises
        ------
            ValueError
                If the analysis database has already been closed, then a ValueError is raised.

        Returns
        -------
            list of str
                Returns a list containing the names of all the clusterings that are contained in this analysis database.
        """

        # Checks if the database has already been closed, in that case a ValueError is raised
        if self.is_closed:
            raise ValueError('The analysis database has already been closed.')

        # Since every analysis contained in this analysis database has its own set of clusterings, the number and the
        # names of the clusterings may vary between analyses, as it is not enforced that they all must have the same
        # clusterings, nevertheless, this assumes that each analysis in a single analysis database has the same
        # clusterings and therefore the names are only retrieved from the first one
        first_category_name = self.get_categories()[0].name
        return list(self.analysis_file[first_category_name]['cluster'])

    def get_embedding_names(self):
        """
        Retrieves the names of all the embeddings that are contained in the analysis database. The embedding names are
        the names of the methods with which the embedding was generated. This will most likely be "spectral" for
        spectral embeddings and "tsne" for a T-SNE embedding.

        Raises
        ------
            ValueError
                If the analysis database has already been closed, then a ValueError is raised.

        Returns
        -------
            list of str
                Returns a list containing the names of all the embeddings that are contained in this analysis database.
        """

        # Checks if the database has already been closed, in that case a ValueError is raised
        if self.is_closed:
            raise ValueError('The analysis database has already been closed.')

        # Since every analysis contained in this analysis database has its own set of embeddings, the number and the
        # names of the embeddings may vary between analyses, as it is not enforced that they all must have the same
        # embeddings, nevertheless, this assumes that each analysis in a single analysis database has the same
        # embeddings and therefore the names are only retrieved from the first one
        first_category_name = self.get_categories()[0].name
        return list(self.analysis_file[first_category_name]['embedding'])

    def has_analysis(self, category_name, clustering_name, embedding_name):
        """
        Determines whether the analysis database contains the analysis with the specified category name (categories can,
        for example, be classes for which the analysis was performed).

        Parameters
        ----------
            category_name: str
                The name of the category for which the analysis was performed. Each analysis was performed for a certain
                subset of the attributions, in most cases this subset will be defined by the label of dataset samples of
                the attributions. So the category name is the umbrella term for all the attributions that comprise the
                analysis, which will, in most cases, be the name/index/WordNet ID of the label.
            clustering_name: str
                On top of the embedding a clustering is performed. This clustering name is the name of the clustering
                that is to be retrieved (because usually the analysis contains multiple different clusterings, which are
                most likely k-means with different k's).
            embedding_name: str
                The name of the embedding that is to be retrieved. This is the name of the method that was used to
                create the embedding. Most likely this will be "spectral" for spectral embeddings and "tsne" for a
                T-SNE embedding.

        Raises
        ------
            ValueError
                If the analysis database has already been closed, then a ValueError is raised.

        Returns
        -------
            bool
                Returns True if the database contains the analysis with the specified name and False otherwise.
        """

        if self.is_closed:
            raise ValueError('The analysis database has already been closed.')

        if category_name not in self.analysis_file.keys():
            return False
        if clustering_name not in self.analysis_file[category_name]['cluster'].keys():
            return False
        return embedding_name in self.analysis_file[category_name]['embedding'].keys()

    def get_analysis(self, category_name, clustering_name, embedding_name):
        """
        Gets the analysis for the specified name (names can be, for example, classes for which the analysis was
        performed).

        Parameters
        ----------
            category_name: str
                The name of the category for which the analysis was performed. Each analysis was performed for a certain
                subset of the attributions, in most cases this subset will be defined by the label of dataset samples of
                the attributions. So the category name is the umbrella term for all the attributions that comprise the
                analysis, which will, in most cases, be the name of the label.
            clustering_name: str
                On top of the embedding a clustering is performed. This clustering name is the name of the clustering
                that is to be retrieved (because usually the analysis contains multiple different clusterings, which are
                most likely k-means with different k's).
            embedding_name: str
                The name of the embedding that is to be retrieved. This is the name of the method that was used to
                create the embedding. Most likely this will be "spectral" for spectral embeddings and "tsne" for a
                T-SNE embedding.

        Raises
        ------
            ValueError
                If the analysis database has already been closed, then a ValueError is raised.
            LookupError
                When the analysis for the specified category name, clustering name, and embedding name could not be
                found, then a LookupError is raised.

        Returns
        -------
            Analysis
                Returns the analysis for the specified name.
        """

        # Checks if the analysis database has already been closed, if so, a ValueError is raised
        if self.is_closed:
            raise ValueError('The analysis database has already been closed.')

        # Checks if the specified analysis exists, if not, then an LookupError is raised
        if not self.has_analysis(category_name, clustering_name, embedding_name):
            raise LookupError(
                'No analysis for category "{0}", clustering "{1}", and embedding "{2}" could be found.'.format(
                    category_name,
                    clustering_name,
                    embedding_name
                )
            )

        # Gets the analysis for the specified name, cluster, and embedding
        analysis = self.analysis_file[category_name]
        clustering = analysis['cluster'][clustering_name]
        embedding = analysis['embedding'][embedding_name]
        attribution_indices = analysis['index']
        eigen_values = None
        if 'eigenvalue' in self.analysis_file[category_name]['embedding'][embedding_name].attrs.keys():
            eigen_values = self.analysis_file[category_name]['embedding'][embedding_name].attrs['eigenvalue']
        base_embedding_name = None
        if 'embedding' in self.analysis_file[category_name]['embedding'][embedding_name].attrs.keys():
            base_embedding_name = self.analysis_file[category_name]['embedding'][embedding_name].attrs['embedding']
            if 'eigenvalue' in self.analysis_file[category_name]['embedding'][base_embedding_name].attrs.keys():
                eigen_values = self.analysis_file[category_name]['embedding'][base_embedding_name].attrs['eigenvalue']
        base_embedding_axes_indices = None
        if 'index' in self.analysis_file[category_name]['embedding'][embedding_name].attrs.keys():
            base_embedding_axes_indices = self.analysis_file[category_name]['embedding'][embedding_name].attrs['index']

        # Wraps the information of the analysis in an object and returns it
        try:
            human_readable_category_name = self.label_map.get_labels(category_name)
        except LookupError:
            human_readable_category_name = category_name
        return Analysis(
            category_name,
            human_readable_category_name,
            clustering_name,
            clustering,
            embedding_name,
            embedding,
            attribution_indices,
            eigen_values,
            base_embedding_name,
            base_embedding_axes_indices
        )

    def close(self):
        """Closes the analysis database."""

        if not self.is_closed:
            if self.analysis_file is not None:
                self.analysis_file.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the analysis database."""

        self.close()


class AnalysisCategory:
    """
    Represents a single category in an analysis. One category can contain many analyses for different attributions. The
    category name is usually an umbrella term for all the attributions contained in the analysis. This is most-likely
    a class name.
    """

    def __init__(self, name, human_readable_name):
        """
        Initializes a new AnalysisCategory instance.

        Parameters
        ----------
            name: str
                The name of the category, e.g. a label index or WordNet ID.
            human_readable_name: str
                A human-readable version of the category name, e.g. the label name.
        """

        self.name = name
        self.human_readable_name = human_readable_name


class Analysis:
    """Represents an analysis of multiple attributions."""

    def __init__(
            self,
            category_name,
            human_readable_category_name,
            clustering_name,
            clustering,
            embedding_name,
            embedding,
            attribution_indices,
            eigen_values,
            base_embedding_name,
            base_embedding_axes_indices
    ):
        """
        Initializes a new Analysis instance.

        Parameters
        ----------
            category_name: str
                The name of the category for which the analysis was performed. Each analysis was performed for a certain
                subset of the attributions, in most cases this subset will be defined by the label of dataset samples of
                the attributions. So the category name is the umbrella term for all the attributions that comprise the
                analysis, which will, in most cases, be the name of the label.
            human_readable_category_name: str
                A human readable version of the category name (since category names are usually label, this can be
                the human-readable name of the label, if the category name is not a label, then the human-readable name
                should be set to the category name itself).
            clustering_name: str
                On top of the embedding a clustering is performed. This clustering name is the name of the clustering
                that is to be retrieved (because usually the analysis contains multiple different clusterings, which are
                most likely k-means with different k's).
            clustering: numpy.ndarray
                The clustering, which is an array that contains for each attribution, that is part of the analysis, the
                number of the cluster to which is belongs.
            embedding_name: str
                The name of the embedding that is to be retrieved. This is the name of the method that was used to
                create the embedding. Most likely this will be "spectral" for spectral embeddings and "tsne" for a
                T-SNE embedding.
            embedding: numpy.ndarray
                The embedding, which contains the embedding vector for all the attributions, that are part of the
                analysis.
            attribution_indices: numpy.ndarray
                Contains a list of the indices of the attributions that correspond to the embeddings and cluster points.
            eigen_values: numpy.ndarray
                The eigen values of the embedding. The eigen values must only be specified for normal embeddings that
                are not based on another embedding (see the description for the base_embedding_name parameter for more
                information).
            base_embedding_name: str
                There are two types of embeddings: normal embeddings and embeddings of embeddings. Embeddings of
                embeddings are embeddings that are based on another embedding (e.g. the spectral embedding has a lot of
                dimensions, so a T-SNE embedding is performed on the spectral embedding, which embeds the spectral
                embedding in two-dimensional space). This is the name of the embedding on which the embedding is based.
                When this is a normal embedding, then this should be None.
            base_embedding_axes_indices: numpy.ndarray
                The indices of the axes of the embedding on which this embedding is based. This value must only be
                specified for embeddings that are based on other embeddings and not normal embeddings (see the
                description for the base_embedding_name parameter for more information).
        """

        self.category_name = category_name
        self.human_readable_category_name = human_readable_category_name
        self.clustering_name = clustering_name
        self.clustering = clustering
        self.embedding_name = embedding_name
        self.embedding = embedding
        self.attribution_indices = attribution_indices
        self.eigen_values = eigen_values
        self.base_embedding_name = base_embedding_name
        self.base_embedding_axes_indices = base_embedding_axes_indices


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
        self.dataset_file = h5py.File(self.path, 'r')

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
            ValueError
                When the dataset has already been closed, then a ValueError is raised.
            LookupError
                When the specified index is out of range, a LookupError is raised.

        Returns
        -------
            Sample
                Returns the sample at the specified index.
        """

        # Checks if the dataset is already closed
        if self.is_closed:
            raise ValueError('The dataset is already closed.')

        # Checks if the index is out of range
        if 'index' in self.dataset_file:
            try:
                data_index = self.dataset_file['index'][index].item()
            except ValueError as error:
                raise LookupError('No sample with the index {0} could be found.'.format(index)) from error
        else:
            data_index = index

        # Extracts the information about the sample from the dataset
        try:
            sample_data = self.dataset_file['data'][data_index][:]
            sample_label_reference = self.dataset_file['label'][index]
            sample_labels = self.label_map.get_labels(sample_label_reference)
        except ValueError as error:
            raise LookupError('No sample with the index {0} could be found.'.format(index)) from error

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
            LookupError
                When the specified index is out of range, a LookupError is raised.

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

        return len(self.dataset_file['data'])

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
            label_index_regex,
            label_word_net_id_regex,
            input_width,
            input_height,
            down_sampling_method,
            up_sampling_method,
            label_map
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
            label_index_regex: str
                A regular expression, which is used to parse the path of a sample for the label index. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or
                label_word_net_id_regex must be specified.
            label_word_net_id_regex: str
                A regular expression, which is used to parse the path of a sample for the WordNet ID. The sample index
                must be captured in the first group. Can be None, but either label_index_regex or
                label_word_net_id_regex must be specified.
            input_width: int
                The width of the input to the model. This is used to resize the dataset samples to the same size as the
                the model expects its inputs to be.
            input_height: int
                The height of the input to the model. This is used to resize the dataset samples to the same size as the
                the model expects its inputs to be.
            down_sampling_method: str
                The method that is to be used to down-sample images from the dataset that are larger than the input to
                the model.
            up_sampling_method: str
                The method that is to be used to up-sample images from the dataset that are smaller than the input to
                the model.
            label_map: LabelMap
                The label map, which contains a mapping between the index of the labels and their human-readable names.

        Raises
        ------
            ValueError
                If the specified up-sampling method is not supported, a ValueError is raised.
                If the specified down-sampling method is not supported, a ValueError is raised.
        """

        # Initializes some class members
        self.is_closed = False

        # Validates the arguments
        if down_sampling_method not in ['none', 'center_crop', 'resize']:
            raise ValueError('The down-sampling method "{0}" is not supported.'.format(down_sampling_method))
        if up_sampling_method not in ['none', 'fill_zeros', 'fill_ones', 'edge_repeat', 'mirror_edge', 'wrap_around',
                                      'resize']:
            raise ValueError('The up-sampling method "{0}" is not supported.'.format(up_sampling_method))

        # Stores the arguments for later reference
        self.name = name
        self.path = path
        self.label_index_regex = label_index_regex
        self.label_word_net_id_regex = label_word_net_id_regex
        self.input_width = input_width
        self.input_height = input_height
        self.down_sampling_method = down_sampling_method
        self.up_sampling_method = up_sampling_method
        self.label_map = label_map

        # Loads a list of all the paths to all samples in the dataset (they are soreted, because the index of the sorted
        # paths corresponds to the sample index that has to be specified in the get_sample method)
        if os.path.exists(self.path + '_paths.txt'):
            with open(self.path + '_paths.txt') as f:
                self.sample_paths = sorted([os.path.join(os.path.dirname(self.path), path)
                                            for path in f.read().split('\n')])
        else:
            self.sample_paths = sorted(glob.glob(os.path.join(self.path, '**/*.*'), recursive=True))
        assert len(self.sample_paths) > 0, 'No Images found.'

    def get_sample(self, index):
        """
        Gets the sample at the specified index.

        Parameters
        ----------
            index: int
                The index of the sample that is to be retrieved.

        Raises
        ------
            ValueError
                If the dataset has already been closed, then a ValueError is raised.
            LookupError
                When the specified index is out of range, a LookupError is raised.
                If the label for the retrieved sample could not be determined from the label lookup, then a LookupError
                is raised

        Returns
        -------
            Sample
                Returns the sample at the specified index.
        """

        # Checks if the dataset is already closed
        if self.is_closed:
            raise ValueError('The dataset is already closed.')

        # Gets the path to the sample file
        if index >= len(self.sample_paths):
            raise LookupError('No sample with the index {0} could be found.'.format(index))
        sample_path = self.sample_paths[index]

        # Determines the label of the sample by parsing the path
        label_reference = None
        if self.label_index_regex is not None:
            match = re.match(self.label_index_regex, sample_path)
            if match:
                label_reference = match.groups()[0]
        else:
            match = re.match(self.label_word_net_id_regex, sample_path)
            if match:
                label_reference = match.groups()[0]
        if label_reference is None:
            raise LookupError('The label for the sample could not be determined based on the label map.')
        label = self.label_map.get_labels(label_reference)

        # Loads the image from file and converts to a NumPy array
        image = Image.open(sample_path).convert('RGB')
        image = numpy.array(image)

        # Performs the re-sampling of the image (depending on whether it is smaller or larger than the target input
        # size, different methods are used, which are specified in the project file)
        image = self.re_sample_image(image)

        # Returns the sample
        return Sample(index, image, label)

    def re_sample_image(self, image):
        """
        Re-samples an image based on the specified up-sampling and down-sampling methods.

        Parameters
        ----------
            image: numpy.ndarray
                The image that is to be re-sampled.

        Returns
        -------
            numpy.ndarray
                Returns the re-sampled image.
        """

        # If at least one of the image dimensions is smaller than the target size, then the image is first up-sampled
        # (if for example the width is smaller than the target width but the height is larger, then the image is first
        # up-sampled so that the width matched the target width, in the next step, the image will be down-sampled, so
        # that the height also matches the target width)
        if len(image.shape) == 2:
            width, height = image.shape
        else:
            width, height, _ = image.shape
        if width < self.input_width or height < self.input_height:
            if self.up_sampling_method in ['fill_zeros', 'fill_ones', 'edge_repeat', 'mirror_edge', 'wrap_around']:
                image = add_border(
                    image,
                    max(width, self.input_width),
                    max(height, self.input_height),
                    self.up_sampling_method
                )
            elif self.up_sampling_method == 'resize':
                image = numpy.array(Image.fromarray(image).resize((self.input_width, self.input_height)))
            elif self.up_sampling_method == 'none':
                pass
            else:
                raise ValueError('The up-sampling method "{0}" is not supported.'.format(self.up_sampling_method))

        # If at least one of the image dimensions is greater than the target size, then the image is down-sampled
        if width > self.input_width or height > self.input_height:
            if self.down_sampling_method == 'center_crop':
                image = center_crop(image, self.input_width, self.input_height)
            elif self.down_sampling_method == 'resize':
                image = numpy.array(Image.fromarray(image).resize((self.input_width, self.input_height)))
            elif self.up_sampling_method == 'none':
                pass
            else:
                raise ValueError('The down-sampling method "{0}" is not supported.'.format(self.down_sampling_method))

        if image.ndim == 2:  # If image black and white add the third axis
            image = image[..., numpy.newaxis]

        # Returns the re-sampled image
        return image

    def __getitem__(self, key):
        """
        Gets the specified sample(s). This implements the Python interface for the []-indexer.

        Parameters
        ----------
            key: int or slice or range or list or tuple or numpy.ndarray
                The key of the sample/samples that are to be retrieved.

        Raises
        ------
            LookupError
                When the specified index is out of range, a LookupError is raised.

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
            labels: str or list
                The label or a list of all the labels that the sample has.
        """

        # Stores the arguments for later use
        self.index = index
        self.data = data
        if not isinstance(labels, list):
            labels = [labels]
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

    def get_labels(self, reference):
        """
        Retrieves the human-readable names of the labels that match the specified reference. The reference may either be
        an index, a n-hot encoded vector, or a WordNet ID, the method will figure out which it is and retrieve the
        correct labels.

        Parameters
        ----------
            reference: int or str or numpy.ndarray
                The reference for which all matching labels are to be retrieved. This can either be an index, a n-hot
                encoded vector, or a WordNet ID.

        Raises
        ------
            LookupError
                When no labels for the specified reference could be found (or one or more in case of a n-hot vector),
                then a LookupError is raised.

        Returns
        -------
            str or list of str
                Returns the human-readable name or a list of all the human-readable names of the labels that matched the
                specified reference.
        """

        if isinstance(reference, numpy.ndarray):
            return self.get_labels_from_n_hot_vector(reference)
        if isinstance(reference, int):
            return self.get_label_from_index(reference)
        if numpy.issubdtype(type(reference), numpy.integer):
            return self.get_label_from_index(reference.item())
        if isinstance(reference, str):
            return self.get_label_from_word_net_id(reference)
        raise LookupError('No labels for the specified reference "{0}" could be found.'.format(reference))

    def get_label_from_index(self, index):
        """
        Retrieves the human-readable name of the label with the specified index.

        Parameters
        ----------
            index: int
                The index of the label.

        Raises
        ------
            LookupError
                If the specified index does not exist, then a LookupError is raised.

        Returns
        -------
            str
                Returns the human-readable name of the label.
        """

        for label in self.labels:
            if label.index == index:
                return label.name
        raise LookupError('No label with the specified index {0} could be found.'.format(index))

    def get_labels_from_n_hot_vector(self, n_hot_vector):
        """
        Retrieves the human-readable names of the labels that are specified by the n-hot encoded vector.

        Parameters
        ----------
            n_hot_vector: numpy.ndarray
                A n-hot encoded vector, where the indices are the label indices and the values are True/1 when the label
                is present and False/0 when the label is not present.

        Raises
        ------
            LookupError
                If the length of the n-hot encoded vector is greater than the number of labels (that is there are
                indices for which there are no labels), then a LookupError is raised.

        Returns
        -------
            list of str
                Returns a list of all the labels that are specified by the n-hot encoded vector.
        """

        try:
            labels = []
            for index in numpy.argwhere(n_hot_vector):
                labels.append(self.get_label_from_index(index[0]))
            return labels
        except LookupError:
            raise LookupError('One or more labels for the n-hot encoded vector do not exist.')

    def get_label_from_word_net_id(self, word_net_id):
        """
        Retrieves the human-readable name of the label with the specified WordNet ID.

        Parameters
        ----------
            word_net_id: str
                The WordNet ID of the label.

        Raises
        ------
            LookupError
                If the specified WordNet ID does not exist, then a LookupError is raised.

        Returns
        -------
            str
                Returns the human-readable name of the label.
        """

        for label in self.labels:
            if label.word_net_id == word_net_id:
                return label.name
        raise LookupError('No label with the specified WordNet ID "{0}" could be found.'.format(word_net_id))


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

        project_names = []
        for project in self.projects:
            project_names.append(project.name)
        return project_names

    def get_project(self, name):
        """
        Retrieves the project with the specified name

        Parameters
        ----------
            name: str
                The name of the project that is to be retrieved.

        Raises
        ------
            ValueError
                If the workspace is already closed, a ValueError is raised.
            LookupError
                If the project with the specified name could not be found, then a LookupError is raised.

        Returns
        -------
            Project
                Returns the project with the specified name.
        """

        # If the workspace is closed, then a ValueError is raised
        if self.is_closed:
            raise ValueError('The workspace is already closed.')

        # Searches for the project with the specified name and returns it if it was found
        for project in self.projects:
            if project.name == name:
                return project

        # If no project with the specified name could not be found, then an exception is raised
        raise LookupError('The project with the name "{0}" could not be found.'.format(name))

    def close(self):
        """Closes the workspace and all projects within it."""

        if not self.is_closed:
            for project in self.projects:
                project.close()
            self.is_closed = True

    def __del__(self):
        """Destructs the workspace."""

        self.close()
