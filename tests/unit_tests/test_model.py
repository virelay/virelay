"""Contains the tests for the model abstractions of ViRelAy."""

import os
import glob

import numpy
import pytest

from virelay.model import (
    DownSamplingMethod,
    Project,
    AttributionDatabase,
    Attribution,
    AnalysisDatabase,
    Analysis,
    AnalysisCategory,
    Hdf5Dataset,
    ImageDirectoryDataset,
    Sample,
    LabelMap,
    Label,
    UpSamplingMethod,
    Workspace
)

NUMBER_OF_CLASSES = 3
NUMBER_OF_SAMPLES = 40


class TestProject:
    """Represents the tests for the Project class."""

    @staticmethod
    def test_project_creation_with_hdf5_dataset(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether a project with an HDF5 dataset can be created.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)
        assert not project.is_closed
        assert project.name == 'Test Project'
        assert project.model == 'No Model'
        assert project.dataset is not None
        assert project.dataset.name == 'HDF5 Dataset'
        assert project.attribution_method == 'Random Attribution'
        assert len(project.analyses) == 1
        assert 'Spectral Analysis' in project.analyses

    @staticmethod
    def test_project_creation_with_image_directory_dataset(project_file_with_image_directory_dataset_path: str) -> None:
        """Tests whether a project with an image directory dataset can be created.

        Args:
            project_file_with_image_directory_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_image_directory_dataset_path)
        assert not project.is_closed
        assert project.name == 'Test Project'
        assert project.model == 'No Model'
        assert project.dataset is not None
        assert project.dataset.name == 'Image Directory Dataset'
        assert project.attribution_method == 'Random Attribution'
        assert len(project.analyses) == 1
        assert 'Spectral Analysis' in project.analyses

    @staticmethod
    def test_project_creation_with_multiple_analysis_databases(project_file_with_multiple_analysis_databases_path: str) -> None:
        """Tests whether a project without attributions or analyses can be created.

        Args:
            project_file_with_multiple_analysis_databases_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_multiple_analysis_databases_path)

        project.get_analysis_methods()
        project.get_analysis_categories('Spectral Analysis')
        project.get_analysis_clustering_names('Spectral Analysis')
        project.get_analysis_embedding_names('Spectral Analysis')
        project.get_analysis('Spectral Analysis', '00000000', 'agglomerative-02', 'spectral')

    @staticmethod
    def test_project_creation_without_attributions_or_analyses(project_file_without_attributions_or_analyses_path: str) -> None:
        """Tests whether a project without attributions or analyses can be created.

        Args:
            project_file_without_attributions_or_analyses_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_without_attributions_or_analyses_path)

        with pytest.raises(LookupError):
            project.get_attribution(0)

        with pytest.raises(LookupError):
            project.get_analysis('analysis-method', 'category-name', 'clustering-name', 'embedding-name')

    @staticmethod
    def test_project_creation_with_unknown_dataset_type(project_file_with_unknown_dataset_type_path: str) -> None:
        """Tests whether creating a project with an unknown dataset type fails.

        Args:
            project_file_with_unknown_dataset_type_path (str): The path to the project file that is used for the tests.
        """

        with pytest.raises(ValueError):
            Project(project_file_with_unknown_dataset_type_path)

    @staticmethod
    def test_project_creation_without_dataset(project_file_without_dataset_path: str) -> None:
        """Tests whether a project without a dataset can be created.

        Args:
            project_file_without_dataset_path (str): The path to the project file that is used for the tests.
        """

        with pytest.raises(ValueError):
            Project(project_file_without_dataset_path)

    @staticmethod
    def test_project_creation_with_broken_project_file(broken_project_file_path: str) -> None:
        """Tests whether creating a project from a broken YAML file fails.

        Args:
            broken_project_file_path (str): The path to the project file that is used for the tests.
        """

        with pytest.raises(ValueError):
            Project(broken_project_file_path)

    @staticmethod
    def test_closed_project_cannot_be_used(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether a project correctly refuses to operate when it was already closed.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)
        project.close()

        with pytest.raises(ValueError):
            project.get_sample(0)

        with pytest.raises(ValueError):
            project.get_attribution(0)

        with pytest.raises(ValueError):
            project.get_analysis_methods()

        with pytest.raises(ValueError):
            project.get_analysis_categories('analysis-method')

        with pytest.raises(ValueError):
            project.get_analysis_clustering_names('analysis-method')

        with pytest.raises(ValueError):
            project.get_analysis_embedding_names('analysis-method')

        with pytest.raises(ValueError):
            project.get_analysis('analysis-method', 'category-name', 'clustering-name', 'embedding-name')

    @staticmethod
    def test_project_can_be_closed_multiple_times(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether a project can be closed multiple times without raising an error.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)
        project.close()
        project.close()

    @staticmethod
    def test_project_with_hdf5_dataset_can_retrieve_sample(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether a sample can be retrieved from a project with an HDF5 dataset.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)

        with pytest.raises(LookupError):
            project.get_sample(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        sample = project.get_sample(0)
        assert sample.index == 0
        assert len(sample.labels) == 1
        assert sample.labels[0].index == 0
        assert sample.labels[0].word_net_id == '00000000'
        assert sample.labels[0].name == 'Class 0'
        assert isinstance(sample.data, numpy.ndarray)
        assert sample.data.shape == (32, 32, 3)
        assert sample.data.dtype == numpy.uint8

    @staticmethod
    def test_project_with_image_directory_dataset_can_retrieve_sample(project_file_with_image_directory_dataset_path: str) -> None:
        """Tests whether a sample can be retrieved from a project with image directory dataset.

        Args:
            project_file_with_image_directory_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_image_directory_dataset_path)

        with pytest.raises(LookupError):
            project.get_sample(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        sample = project.get_sample(0)
        assert sample.index == 0
        assert len(sample.labels) == 1
        assert sample.labels[0].index == 0
        assert sample.labels[0].word_net_id == '00000000'
        assert sample.labels[0].name == 'Class 0'
        assert isinstance(sample.data, numpy.ndarray)
        assert sample.data.shape == (64, 64, 3)
        assert sample.data.dtype == numpy.uint8

    @staticmethod
    def test_project_can_retrieve_attribution(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether an attribution can be retrieved from the project.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)

        with pytest.raises(LookupError):
            project.get_attribution(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        attribution = project.get_attribution(0)
        assert attribution.index == 0
        assert len(attribution.labels) == 1
        assert attribution.labels[0].index == 0
        assert attribution.labels[0].word_net_id == '00000000'
        assert attribution.labels[0].name == 'Class 0'
        assert isinstance(attribution.data, numpy.ndarray)
        assert attribution.data.shape == (32, 32, 3)
        assert attribution.data.dtype == numpy.float32
        assert isinstance(attribution.prediction, numpy.ndarray)
        assert attribution.prediction.shape == (NUMBER_OF_CLASSES,)
        assert attribution.prediction.dtype == numpy.float32

    @staticmethod
    def test_project_can_retrieve_analysis_methods(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether a analysis methods can be retrieved from the project.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)
        analysis_methods = project.get_analysis_methods()
        assert len(analysis_methods) == 1
        assert analysis_methods[0] == 'Spectral Analysis'

    @staticmethod
    def test_project_can_retrieve_analysis_categories(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether an analysis categories can be retrieved from the project.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)

        with pytest.raises(LookupError):
            project.get_analysis_categories('Unknown Analysis Method')

        categories = project.get_analysis_categories('Spectral Analysis')
        for category, label in zip(categories, project.label_map.labels):
            assert category.name == label.word_net_id
            assert category.human_readable_name == label.name

    @staticmethod
    def test_project_can_retrieve_analysis_clustering_names(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether an analysis clustering names can be retrieved from the project.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)

        with pytest.raises(LookupError):
            project.get_analysis_clustering_names('Unknown Analysis Method')

        clustering_names = project.get_analysis_clustering_names('Spectral Analysis')
        assert clustering_names[0] == 'agglomerative-02'
        assert clustering_names[1] == 'agglomerative-03'
        assert clustering_names[2] == 'dbscan-eps=0.2'
        assert clustering_names[3] == 'dbscan-eps=0.3'
        assert clustering_names[4] == 'hdbscan'
        assert clustering_names[5] == 'kmeans-02'
        assert clustering_names[6] == 'kmeans-03'

    @staticmethod
    def test_project_can_retrieve_analysis_embedding_names(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether an analysis embedding names can be retrieved from the project.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)

        with pytest.raises(LookupError):
            project.get_analysis_embedding_names('Unknown Analysis Method')

        expected_embedding_names = ['spectral', 'tsne', 'umap']
        actual_embedding_names = project.get_analysis_embedding_names('Spectral Analysis')
        for expected_embedding_name, actual_embedding_name in zip(expected_embedding_names, actual_embedding_names):
            assert expected_embedding_name == actual_embedding_name

    @staticmethod
    def test_project_can_retrieve_analyses(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether analyses can be retrieved from the project.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used for the tests.
        """

        project = Project(project_file_with_hdf5_dataset_path)

        with pytest.raises(LookupError):
            project.get_analysis(
                'unknown-analysis-method',
                'unknown-category',
                'unknown-clustering',
                'unknown-embedding'
            )
        with pytest.raises(LookupError):
            project.get_analysis('Spectral Analysis', 'unknown-category', 'unknown-clustering', 'unknown-embedding')
        with pytest.raises(LookupError):
            project.get_analysis('Spectral Analysis', '00000000', 'unknown-clustering', 'unknown-embedding')
        with pytest.raises(LookupError):
            project.get_analysis('Spectral Analysis', '00000000', 'agglomerative-02', 'unknown-embedding')

        analysis = project.get_analysis('Spectral Analysis', '00000000', 'agglomerative-02', 'spectral')
        assert analysis.category_name == '00000000'
        assert analysis.human_readable_category_name == 'Class 0'
        assert analysis.clustering_name == 'agglomerative-02'
        assert analysis.embedding_name == 'spectral'
        assert isinstance(analysis.clustering, numpy.ndarray)
        assert analysis.clustering.shape == (40,)
        assert analysis.clustering.dtype == numpy.int32
        assert isinstance(analysis.embedding, numpy.ndarray)
        assert analysis.embedding.shape == (40, 32)
        assert analysis.embedding.dtype == numpy.float32
        assert isinstance(analysis.attribution_indices, numpy.ndarray)
        assert analysis.attribution_indices.shape == (40,)
        assert analysis.attribution_indices.dtype == numpy.uint32
        assert isinstance(analysis.eigenvalues, numpy.ndarray)
        assert analysis.eigenvalues.shape == (32,)
        assert analysis.eigenvalues.dtype == numpy.float32


class TestAttributionDatabase:
    """Represents the tests for the AttributionDatabase class."""

    @staticmethod
    def test_attribution_database_creation(attribution_file_path: str, label_map_file_path: str) -> None:
        """Tests whether an attribution database can be created.

        Args:
            attribution_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        attribution_database = AttributionDatabase(attribution_file_path, label_map)
        assert not attribution_database.is_closed
        assert not attribution_database.is_multi_label

    @staticmethod
    def test_closed_attribution_database_cannot_get_attributions(attribution_file_path: str, label_map_file_path: str) -> None:
        """Tests whether the attribution database correctly refuses to operate when it was already closed.

        Args:
            attribution_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        attribution_database = AttributionDatabase(attribution_file_path, label_map)
        attribution_database.close()

        with pytest.raises(ValueError):
            attribution_database.has_attribution(0)

        with pytest.raises(ValueError):
            attribution_database.get_attribution(0)

    @staticmethod
    def test_attribution_database_can_be_closed_multiple_times(attribution_file_path: str, label_map_file_path: str) -> None:
        """Tests whether the attribution database can be closed multiple times without raising an error.

        Args:
            attribution_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        attribution_database = AttributionDatabase(attribution_file_path, label_map)
        attribution_database.close()
        attribution_database.close()

    @staticmethod
    def test_attribution_database_can_check_whether_attribution_is_available(attribution_file_path: str, label_map_file_path: str) -> None:
        """Tests whether it can be checked if the attribution database contains a specific attribution.

        Args:
            attribution_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        attribution_database = AttributionDatabase(attribution_file_path, label_map)

        assert attribution_database.has_attribution(0)
        assert not attribution_database.has_attribution(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

    @staticmethod
    def test_attribution_database_with_sample_indices_can_check_whether_attribution_is_available(
            attribution_file_with_sample_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether it can be checked if the attribution database contains a specific attribution.

        Args:
            attribution_file_with_sample_indices_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        attribution_database = AttributionDatabase(attribution_file_with_sample_indices_path, label_map)

        assert attribution_database.has_attribution(0)
        assert not attribution_database.has_attribution(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

    @staticmethod
    def test_attribution_database_can_retrieve_attribution(attribution_file_path: str, label_map_file_path: str) -> None:
        """Tests whether an attribution can be retrieved from the attribution database.

        Args:
            attribution_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        attribution_database = AttributionDatabase(attribution_file_path, label_map)

        with pytest.raises(LookupError):
            attribution_database.get_attribution(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        attribution = attribution_database.get_attribution(0)
        assert attribution.index == 0
        assert isinstance(attribution.data, numpy.ndarray)
        assert attribution.data.shape == (32, 32, 3)
        assert attribution.data.dtype == numpy.float32
        assert len(attribution.labels) == 1
        assert attribution.labels[0].index == 0
        assert attribution.labels[0].word_net_id == '00000000'
        assert attribution.labels[0].name == 'Class 0'
        assert isinstance(attribution.prediction, numpy.ndarray)
        assert attribution.prediction.shape == (NUMBER_OF_CLASSES,)
        assert attribution.prediction.dtype == numpy.float32

    @staticmethod
    def test_attribution_database_with_sample_indices_can_retrieve_attribution(
            attribution_file_with_sample_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether an attribution can be retrieved from an attribution database that contains sample indices.

        Args:
            attribution_file_with_sample_indices_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        attribution_database = AttributionDatabase(attribution_file_with_sample_indices_path, label_map)

        with pytest.raises(LookupError):
            attribution_database.get_attribution(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        attribution = attribution_database.get_attribution(0)
        assert attribution.index == 0
        assert isinstance(attribution.data, numpy.ndarray)
        assert attribution.data.shape == (32, 32, 3)
        assert attribution.data.dtype == numpy.float32
        assert len(attribution.labels) == 1
        assert attribution.labels[0].index == 0
        assert attribution.labels[0].word_net_id == '00000000'
        assert attribution.labels[0].name == 'Class 0'
        assert isinstance(attribution.prediction, numpy.ndarray)
        assert attribution.prediction.shape == (NUMBER_OF_CLASSES,)
        assert attribution.prediction.dtype == numpy.float32


class TestAttribution:
    """Represents the tests for the Attribution class."""

    @staticmethod
    def test_attribution_creation() -> None:
        """Tests whether an attribution can be created."""

        data = numpy.random.uniform(-1, 1, size=(32, 32, 3))
        label_0 = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label_0, prediction)

        assert attribution.index == 0
        assert numpy.array_equal(attribution.data, data)
        assert attribution.labels == [label_0]
        assert numpy.array_equal(attribution.prediction, prediction)

        data = numpy.random.uniform(-1, 1, size=(32, 32, 3))
        label_1 = Label(1, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(1, data, [label_0, label_1], prediction)

        assert attribution.index == 1
        assert numpy.array_equal(attribution.data, data)
        assert attribution.labels == [label_0, label_1]
        assert numpy.array_equal(attribution.prediction, prediction)

        data = numpy.random.uniform(-1, 1, size=(3, 32, 32))
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(2, data, label_0, prediction)

        assert attribution.index == 2
        assert numpy.array_equal(attribution.data, numpy.moveaxis(data, [0, 1, 2], [2, 0, 1]))
        assert attribution.labels == [label_0]
        assert numpy.array_equal(attribution.prediction, prediction)

    @staticmethod
    def test_attribution_render_heatmap_unknown_color_map() -> None:
        """Tests whether the heatmap rendering of the attribution fails, when the color map is unknown."""

        data = numpy.random.uniform(-1, 1, size=(4, 4, 3))
        label = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label, prediction)
        with pytest.raises(ValueError):
            attribution.render_heatmap('unknown-color-map')

    @staticmethod
    def test_attribution_render_heatmap() -> None:
        """Tests whether a heatmap can be rendered from the attribution."""

        # Creates the attribution
        data = numpy.array(
            [[[-0.63598313, 0.05182445, -0.94523354],
              [0.21506858, -0.13204615, 0.0819828],
              [0.10219199, -0.49505036, -0.57652793],
              [0.01718352, 0.0409061, 0.58327392]],
             [[0.86893207, -0.26937166, -0.94142186],
              [-0.61266463, -0.09961933, -0.80746353],
              [-0.91493128, -0.31382453, 0.04481068],
              [-0.39876502, -0.28151701, 0.93280041]],
             [[0.28490411, 0.47067797, 0.40586151],
              [-0.3422943, 0.91319999, -0.98634023],
              [0.81298836, 0.39517061, 0.76021407],
              [0.10702649, -0.62526615, -0.34403102]],
             [[-0.27316466, 0.93960925, 0.03727774],
              [0.83324282, -0.69104866, 0.50410142],
              [0.86643333, 0.50700986, 0.16282292],
              [-0.71744439, 0.27219448, 0.34797268]]]
        )
        label = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label, prediction)

        # Validates the colors assigned by the heatmap
        expected_heatmap = numpy.array(
            [[[56, 56, 255],
              [255, 234, 234],
              [128, 128, 255],
              [255, 172, 172]],
             [[210, 210, 255],
              [58, 58, 255],
              [102, 102, 255],
              [255, 222, 222]],
             [[255, 104, 104],
              [200, 200, 255],
              [255, 0, 0],
              [142, 142, 255]],
             [[255, 163, 163],
              [255, 170, 170],
              [255, 56, 56],
              [242, 242, 255]]],
            dtype=numpy.uint8
        )
        actual_heatmap = attribution.render_heatmap('blue-white-red')
        assert numpy.array_equal(expected_heatmap, actual_heatmap)

    @staticmethod
    def test_attribution_render_superimposed_heatmap_unknown_color_map() -> None:
        """Tests the rendering of heatmap images that are then superimposed onto another image using the attribution data as alpha-channel using an
        unknown color map.
        """

        data = numpy.random.uniform(-1, 1, size=(4, 4, 3))
        label = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label, prediction)
        superimpose = numpy.ones((4, 4, 3))
        with pytest.raises(ValueError):
            attribution.render_heatmap('unknown-color-map', superimpose)

    @staticmethod
    def test_attribution_render_superimposed_heatmap() -> None:
        """Tests whether a heatmap, superimposed onto another image, can be rendered from the attribution."""

        # Creates the attribution
        data = numpy.array(
            [[[0.17681855, 0.91944598, 0.33373127],
              [-0.80632149, -0.93380861, 0.15624767],
              [-0.80029563, -0.10224675, -0.21737921],
              [-0.12587663, 0.00244791, 0.0558195]],
             [[0.34478494, 0.22592281, -0.46938452],
              [-0.28683651, -0.43241806, -0.74974368],
              [0.28910623, 0.9201011, 0.69483512],
              [0.60624353, 0.58788177, 0.05531979]],
             [[-0.52632942, 0.95181703, -0.12907603],
              [0.11709027, -0.78199527, -0.3564949],
              [-0.02690579, 0.30163809, 0.15051245],
              [0.29140564, 0.79343594, -0.43470242]],
             [[-0.43761021, 0.27552307, 0.028462],
              [-0.37463762, -0.09987923, 0.65990991],
              [0.46209578, 0.72126955, 0.50027807],
              [0.68741856, 0.13709213, 0.92287532]]]
        )
        label = Label(0, '00000000', 'Class 0')
        prediction = numpy.random.uniform(0, 1, size=(NUMBER_OF_CLASSES, ))
        attribution = Attribution(0, data, label, prediction)
        superimpose = numpy.ones((4, 4, 3))

        # Validates the colors assigned by the heatmap
        expected_heatmap = numpy.array(
            [[[172, 42, 42],
              [32, 32, 190],
              [55, 55, 134],
              [9, 9, 9]],
             [[13, 12, 12],
              [41, 41, 177],
              [229, 0, 0],
              [150, 52, 52]],
             [[36, 31, 31],
              [57, 57, 124],
              [52, 40, 40],
              [79, 52, 52]],
             [[16, 16, 17],
              [23, 21, 21],
              [202, 22, 22],
              [210, 17, 17]]],
            dtype=numpy.uint8
        )
        actual_heatmap = attribution.render_heatmap('blue-white-red', superimpose)
        assert numpy.array_equal(expected_heatmap, actual_heatmap)


class TestAnalysisDatabase:
    """Represents the tests for the AnalysisDatabase class."""

    @staticmethod
    def test_analysis_database_creation(spectral_analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether an analysis database can be created.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)
        assert not analysis_database.is_closed

    @staticmethod
    def test_closed_analysis_database_cannot_be_used(spectral_analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether the analysis database correctly refuses to operate when it was already closed.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)
        analysis_database.close()

        with pytest.raises(ValueError):
            analysis_database.get_categories()

        with pytest.raises(ValueError):
            analysis_database.get_clustering_names()

        with pytest.raises(ValueError):
            analysis_database.get_embedding_names()

        with pytest.raises(ValueError):
            analysis_database.has_analysis('category-name', 'clustering-name', 'embedding-name')

        with pytest.raises(ValueError):
            analysis_database.get_analysis('category-name', 'clustering-name', 'embedding-name')

    @staticmethod
    def test_analysis_database_can_be_closed_multiple_times(spectral_analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether the analysis database can be closed multiple times without raising an error.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)
        analysis_database.close()
        analysis_database.close()

    @staticmethod
    def test_analysis_database_can_retrieve_categories(spectral_analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether categories can be retrieved from the analysis database.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)
        categories = analysis_database.get_categories()
        for category, label in zip(categories, label_map.labels):
            assert category.name == label.word_net_id
            assert category.human_readable_name == label.name

    @staticmethod
    def test_analysis_database_can_retrieve_categories_with_missing_labels_in_label_map(
            spectral_analysis_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether categories can be retrieved from the analysis database, even if the human-readable category names cannot be retrieved from
        the label map.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        label_map.labels = []
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)
        categories = analysis_database.get_categories()
        for category, label in zip(categories, label_map.labels):
            assert category.name == label.word_net_id
            assert category.human_readable_name == ''

    @staticmethod
    def test_analysis_database_can_retrieve_clustering_names(spectral_analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether clustering names can be retrieved from the analysis database.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)
        expected_clustering_names = [
            'agglomerative-02',
            'agglomerative-03',
            'dbscan-eps=0.2',
            'dbscan-eps=0.3',
            'hdbscan',
            'kmeans-02',
            'kmeans-03'
        ]
        actual_clustering_names = analysis_database.get_clustering_names()
        for expected_clustering_name, actual_clustering_name in zip(expected_clustering_names, actual_clustering_names):
            assert expected_clustering_name == actual_clustering_name

    @staticmethod
    def test_analysis_database_can_retrieve_embedding_names(spectral_analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether embedding names can be retrieved from the analysis database.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)
        expected_embedding_names = ['spectral', 'tsne', 'umap']
        actual_embedding_names = analysis_database.get_embedding_names()
        for expected_embedding_name, actual_embedding_name in zip(expected_embedding_names, actual_embedding_names):
            assert expected_embedding_name == actual_embedding_name

    @staticmethod
    def test_analysis_database_can_check_whether_analysis_is_available(spectral_analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether it can be checked if the analysis database contains a specific analysis.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)

        assert not analysis_database.has_analysis('unknown-category', 'unknown-clustering', 'unknown-embedding')
        assert not analysis_database.has_analysis('00000000', 'unknown-clustering', 'unknown-embedding')
        assert not analysis_database.has_analysis('00000000', 'agglomerative-02', 'unknown-embedding')
        assert analysis_database.has_analysis('00000000', 'agglomerative-02', 'spectral')

    @staticmethod
    def test_analysis_database_can_retrieve_analyses(spectral_analysis_file_path: str, label_map_file_path: str) -> None:
        """Tests whether analyses can be retrieved from the analysis database.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)

        with pytest.raises(LookupError):
            analysis_database.get_analysis('unknown-category', 'unknown-clustering', 'unknown-embedding')
        with pytest.raises(LookupError):
            analysis_database.get_analysis('00000000', 'unknown-clustering', 'unknown-embedding')
        with pytest.raises(LookupError):
            analysis_database.get_analysis('00000000', 'agglomerative-02', 'unknown-embedding')

        analysis = analysis_database.get_analysis('00000000', 'agglomerative-02', 'spectral')
        assert analysis.category_name == '00000000'
        assert analysis.human_readable_category_name == 'Class 0'
        assert analysis.clustering_name == 'agglomerative-02'
        assert analysis.embedding_name == 'spectral'
        assert isinstance(analysis.clustering, numpy.ndarray)
        assert analysis.clustering.shape == (40,)
        assert analysis.clustering.dtype == numpy.int32
        assert isinstance(analysis.embedding, numpy.ndarray)
        assert analysis.embedding.shape == (40, 32)
        assert analysis.embedding.dtype == numpy.float32
        assert isinstance(analysis.attribution_indices, numpy.ndarray)
        assert analysis.attribution_indices.shape == (40,)
        assert analysis.attribution_indices.dtype == numpy.uint32
        assert isinstance(analysis.eigenvalues, numpy.ndarray)
        assert analysis.eigenvalues.shape == (32,)
        assert analysis.eigenvalues.dtype == numpy.float32

    @staticmethod
    def test_analysis_database_can_retrieve_analyses_with_missing_labels_in_label_map(
            spectral_analysis_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether analyses can be retrieved from the analysis database, even if the human-readable category names cannot be retrieved from the
        label map.

        Args:
            spectral_analysis_file_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        label_map.labels = []
        analysis_database = AnalysisDatabase(spectral_analysis_file_path, label_map)

        with pytest.raises(LookupError):
            analysis_database.get_analysis('unknown-category', 'unknown-clustering', 'unknown-embedding')
        with pytest.raises(LookupError):
            analysis_database.get_analysis('00000000', 'unknown-clustering', 'unknown-embedding')
        with pytest.raises(LookupError):
            analysis_database.get_analysis('00000000', 'agglomerative-02', 'unknown-embedding')

        analysis = analysis_database.get_analysis('00000000', 'agglomerative-02', 'spectral')
        assert analysis.category_name == '00000000'
        assert analysis.human_readable_category_name == ''
        assert analysis.clustering_name == 'agglomerative-02'
        assert analysis.embedding_name == 'spectral'
        assert isinstance(analysis.clustering, numpy.ndarray)
        assert analysis.clustering.shape == (40,)
        assert analysis.clustering.dtype == numpy.int32
        assert isinstance(analysis.embedding, numpy.ndarray)
        assert analysis.embedding.shape == (40, 32)
        assert analysis.embedding.dtype == numpy.float32
        assert isinstance(analysis.attribution_indices, numpy.ndarray)
        assert analysis.attribution_indices.shape == (40,)
        assert analysis.attribution_indices.dtype == numpy.uint32
        assert isinstance(analysis.eigenvalues, numpy.ndarray)
        assert analysis.eigenvalues.shape == (32,)
        assert analysis.eigenvalues.dtype == numpy.float32

    @staticmethod
    def test_analysis_database_can_retrieve_analyses_without_eigenvalues(
            spectral_analysis_file_without_eigenvalues_path: str,
            label_map_file_path: str) -> None:
        """Tests whether analyses can be retrieved from the analysis database that does not contain eigenvalues.

        Args:
            spectral_analysis_file_without_eigenvalues_path (str): The path to the attributions file that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        analysis_database = AnalysisDatabase(spectral_analysis_file_without_eigenvalues_path, label_map)

        with pytest.raises(LookupError):
            analysis_database.get_analysis('unknown-category', 'unknown-clustering', 'unknown-embedding')
        with pytest.raises(LookupError):
            analysis_database.get_analysis('00000000', 'unknown-clustering', 'unknown-embedding')
        with pytest.raises(LookupError):
            analysis_database.get_analysis('00000000', 'agglomerative-02', 'unknown-embedding')

        analysis = analysis_database.get_analysis('00000000', 'agglomerative-02', 'spectral')
        assert analysis.category_name == '00000000'
        assert analysis.human_readable_category_name == 'Class 0'
        assert analysis.clustering_name == 'agglomerative-02'
        assert analysis.embedding_name == 'spectral'
        assert isinstance(analysis.clustering, numpy.ndarray)
        assert analysis.clustering.shape == (40,)
        assert analysis.clustering.dtype == numpy.int32
        assert isinstance(analysis.embedding, numpy.ndarray)
        assert analysis.embedding.shape == (40, 32)
        assert analysis.embedding.dtype == numpy.float32
        assert isinstance(analysis.attribution_indices, numpy.ndarray)
        assert analysis.attribution_indices.shape == (40,)
        assert analysis.attribution_indices.dtype == numpy.uint32
        assert analysis.eigenvalues is None


class TestAnalysisCategory:
    """Represents the tests for the AnalysisCategory class."""

    @staticmethod
    def test_analysis_category_creation() -> None:
        """Tests whether an analysis category can be created."""

        analysis_category = AnalysisCategory('class-0', 'Class 0')
        assert analysis_category.name == 'class-0'
        assert analysis_category.human_readable_name == 'Class 0'


class TestAnalysis:
    """Represents the tests for the Analysis class."""

    @staticmethod
    def test_analysis_creation() -> None:
        """Tests whether an analysis can be created."""

        clustering = numpy.random.randint(NUMBER_OF_CLASSES, size=NUMBER_OF_SAMPLES)
        embedding = numpy.random.uniform(size=(NUMBER_OF_CLASSES, 16))
        attribution_indices = numpy.random.randint(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES, size=NUMBER_OF_SAMPLES)
        eigenvalues = numpy.random.normal(size=NUMBER_OF_SAMPLES)
        analysis = Analysis(
            category_name='class-0',
            human_readable_category_name='Class 0',
            clustering_name='kmeans-2',
            clustering=clustering,
            embedding_name='spectral',
            embedding=embedding,
            attribution_indices=attribution_indices,
            eigenvalues=eigenvalues
        )

        assert analysis.category_name == 'class-0'
        assert analysis.human_readable_category_name == 'Class 0'
        assert analysis.clustering_name == 'kmeans-2'
        assert numpy.array_equal(analysis.clustering, clustering)
        assert analysis.embedding_name == 'spectral'
        assert numpy.array_equal(analysis.embedding, embedding)
        assert numpy.array_equal(analysis.attribution_indices, attribution_indices)
        assert analysis.eigenvalues is not None
        assert numpy.array_equal(analysis.eigenvalues, eigenvalues)


class TestHdf5Dataset:
    """Represents the tests for the Hdf5Dataset class."""

    @staticmethod
    def test_dataset_has_correct_size(hdf5_dataset_file_path: str, label_map_file_path: str) -> None:
        """Tests whether the dataset correctly reports its size/length.

        Args:
            hdf5_dataset_file_path (str): The path to the HDF5 dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=hdf5_dataset_file_path,
            label_map=label_map
        )
        assert len(hdf5_dataset) == NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES

    @staticmethod
    def test_closed_dataset_cannot_retrieve_sample(hdf5_dataset_file_path: str, label_map_file_path: str) -> None:
        """Tests whether the dataset correctly refuses to return a sample for a closed dataset.

        Args:
            hdf5_dataset_file_path (str): The path to the HDF5 dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=hdf5_dataset_file_path,
            label_map=label_map
        )
        hdf5_dataset.close()

        with pytest.raises(ValueError):
            hdf5_dataset.get_sample(0)

        with pytest.raises(ValueError):
            _ = hdf5_dataset[0]

    @staticmethod
    def test_dataset_can_be_closed_multiple_times(hdf5_dataset_file_path: str, label_map_file_path: str) -> None:
        """Tests whether the dataset can be closed multiple times without raising an error.

        Args:
            hdf5_dataset_file_path (str): The path to the HDF5 dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=hdf5_dataset_file_path,
            label_map=label_map
        )
        hdf5_dataset.close()
        hdf5_dataset.close()

    @staticmethod
    def test_dataset_cannot_retrieve_sample_for_out_of_bounds_index(hdf5_dataset_file_path: str, label_map_file_path: str) -> None:
        """Tests whether the dataset correctly raises an exception, when a sample is to be retrieved that is not in the dataset.

        Args:
            hdf5_dataset_file_path (str): The path to the HDF5 dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=hdf5_dataset_file_path,
            label_map=label_map
        )

        with pytest.raises(LookupError):
            hdf5_dataset.get_sample(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        with pytest.raises(LookupError):
            _ = hdf5_dataset[NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES]

    @staticmethod
    def test_dataset_can_retrieve_samples(hdf5_dataset_file_path: str, label_map_file_path: str) -> None:
        """Tests whether a sample can be retrieved from the dataset.

        Args:
            hdf5_dataset_file_path (str): The path to the HDF5 dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=hdf5_dataset_file_path,
            label_map=label_map
        )

        sample = hdf5_dataset.get_sample(0)
        assert sample.index == 0
        assert len(sample.labels) == 1
        assert sample.labels[0].index == 0
        assert sample.labels[0].word_net_id == '00000000'
        assert sample.labels[0].name == 'Class 0'
        assert isinstance(sample.data, numpy.ndarray)
        assert sample.data.shape == (32, 32, 3)
        assert sample.data.dtype == numpy.uint8

    @staticmethod
    def test_dataset_can_retrieve_multiple_samples(hdf5_dataset_file_path: str, label_map_file_path: str) -> None:
        """Tests whether multiple samples can be retrieved at the same time.

        Args:
            hdf5_dataset_file_path (str): The path to the HDF5 dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        hdf5_dataset = Hdf5Dataset(
            name="Test Dataset",
            path=hdf5_dataset_file_path,
            label_map=label_map
        )

        samples = hdf5_dataset[2:6]
        assert isinstance(samples, list)
        assert len(samples) == 4

        samples = hdf5_dataset[[2, 10, 12, 20, 19]]
        assert isinstance(samples, list)
        assert len(samples) == 5

        samples = hdf5_dataset[(8, 13, 27)]
        assert isinstance(samples, list)
        assert len(samples) == 3

        samples = hdf5_dataset[numpy.array([21, 4])]
        assert isinstance(samples, list)
        assert len(samples) == 2

        samples = hdf5_dataset[range(10)]
        assert isinstance(samples, list)
        assert len(samples) == 10


class TestImageDirectoryDataset:
    """Represents the tests for the ImageDirectoryDataset class."""

    @staticmethod
    def test_dataset_has_correct_size(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether the dataset correctly reports its size/length.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        assert len(image_directory_dataset) == NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES

    @staticmethod
    def test_unsupported_sampling_methods(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether the constructor of the image directory dataset properly raises an exception if an unsupported sampling method is specified.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        with pytest.raises(ValueError):
            ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=r'^.*/label-([0-9]+)/.*$',
                label_word_net_id_regex=None,
                input_width=64,
                input_height=64,
                down_sampling_method='unsupported',  # type: ignore
                up_sampling_method='none',
                label_map=label_map
            )

        with pytest.raises(ValueError):
            ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=None,
                label_word_net_id_regex=r'^.*/wordnet-([0-9]+)/.*$',
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='unsupported',  # type: ignore
                label_map=label_map
            )

    @staticmethod
    def test_only_one_label_regex_must_be_specified(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether the constructor correctly checks if only one of the possible label RegEx's was specified.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        with pytest.raises(ValueError):
            ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=None,
                label_word_net_id_regex=None,
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='none',
                label_map=label_map
            )

        with pytest.raises(ValueError):
            ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=r'^.*/label-([0-9]+)/.*$',
                label_word_net_id_regex=r'^.*/wordnet-([0-9]+)/.*$',
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='none',
                label_map=label_map
            )

    @staticmethod
    def test_closed_dataset_cannot_retrieve_sample(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether the dataset correctly refuses to return a sample for a closed dataset.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        image_directory_dataset.close()

        with pytest.raises(ValueError):
            image_directory_dataset.get_sample(0)

        with pytest.raises(ValueError):
            _ = image_directory_dataset[0]

    @staticmethod
    def test_dataset_cannot_retrieve_sample_for_out_of_bounds_index(
            image_directory_dataset_with_label_indices_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the dataset correctly raises an exception, when a sample is to be retrieved that is not in the dataset.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )

        with pytest.raises(LookupError):
            image_directory_dataset.get_sample(NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES)

        with pytest.raises(LookupError):
            _ = image_directory_dataset[NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES]

    @staticmethod
    def test_dataset_sample_paths_file(
            image_directory_dataset_with_sample_paths_file_path: str,
            label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can locate samples.

        Args:
            image_directory_dataset_with_sample_paths_file_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_sample_paths_file_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )

        # Only every second sample was added to the sample paths file, so the number of samples in the image directory
        # dataset should be only half of the number of images in the dataset directory
        number_of_images_in_dataset_directory = len(glob.glob(
            os.path.join(image_directory_dataset_with_sample_paths_file_path, '**/*.*'),
            recursive=True
        ))
        assert number_of_images_in_dataset_directory == NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES
        assert len(image_directory_dataset) == number_of_images_in_dataset_directory // 2

    @staticmethod
    def test_dataset_label_index_directory_name(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can properly parse the labels from directory that contain the index of the respective label.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        image_directory_dataset.get_sample(0)

    @staticmethod
    def test_dataset_label_wordnet_id_directory_name(image_directory_dataset_with_wordnet_ids_path: str, label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can properly parse the labels from directory that contain the index of the respective label.

        Args:
            image_directory_dataset_with_wordnet_ids_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_wordnet_ids_path,
            label_index_regex=None,
            label_word_net_id_regex=r'^.*/wordnet-([0-9]+)/.*$',
            input_width=64,
            input_height=64,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        image_directory_dataset.get_sample(0)

    @staticmethod
    def test_dataset_cannot_determine_labels(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether the image directory dataset raises an exception, if it cannot determine the label of a sample, e.g., if the label index or
        WordNet ID RegEx's are incorrect.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        with pytest.raises(LookupError):
            image_directory_dataset = ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=r'^.*/incorrect-([0-9]+)/.*$',
                label_word_net_id_regex=None,
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='none',
                label_map=label_map
            )
            image_directory_dataset.get_sample(0)

        with pytest.raises(LookupError):
            image_directory_dataset = ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=None,
                label_word_net_id_regex=r'^.*/incorrect-([0-9]+)/.*$',
                input_width=64,
                input_height=64,
                down_sampling_method='none',
                up_sampling_method='none',
                label_map=label_map
            )
            image_directory_dataset.get_sample(0)

    @staticmethod
    def test_dataset_down_sampling_methods(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can properly down-sample the images to the correct input size, using all supported down-sampling
        methods.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        # Checks if the dataset does nothing, when no down-sampling is specified, even if the images are too large
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=32,
            input_height=32,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        sample = image_directory_dataset.get_sample(0)
        assert sample.data.shape[0] == 64
        assert sample.data.shape[1] == 64

        # Checks all down-sampling methods
        down_sampling_method: DownSamplingMethod
        down_sampling_methods: list[DownSamplingMethod] = ['center_crop', 'resize']
        for down_sampling_method in down_sampling_methods:
            image_directory_dataset = ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=r'^.*/label-([0-9]+)/.*$',
                label_word_net_id_regex=None,
                input_width=32,
                input_height=32,
                down_sampling_method=down_sampling_method,
                up_sampling_method='none',
                label_map=label_map
            )
            sample = image_directory_dataset.get_sample(0)
            assert sample.data.shape[0] == 32
            assert sample.data.shape[1] == 32

    @staticmethod
    def test_dataset_up_sampling_methods(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether the image directory dataset can properly up-sample the images to the correct input size, using all supported up-sampling
        methods.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        # Checks if the dataset does nothing, when no up-sampling is specified, even if the images are too small
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=128,
            input_height=128,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )
        sample = image_directory_dataset.get_sample(0)
        assert sample.data.shape[0] == 64
        assert sample.data.shape[1] == 64

        # Checks all down-sampling methods
        up_sampling_method: UpSamplingMethod
        up_sampling_methods: list[UpSamplingMethod] = ['fill_zeros', 'fill_ones', 'edge_repeat', 'mirror_edge', 'wrap_around', 'resize']
        for up_sampling_method in up_sampling_methods:
            image_directory_dataset = ImageDirectoryDataset(
                name="Test Dataset",
                path=image_directory_dataset_with_label_indices_path,
                label_index_regex=r'^.*/label-([0-9]+)/.*$',
                label_word_net_id_regex=None,
                input_width=128,
                input_height=128,
                down_sampling_method='none',
                up_sampling_method=up_sampling_method,
                label_map=label_map
            )
            sample = image_directory_dataset.get_sample(0)
            assert sample.data.shape[0] == 128
            assert sample.data.shape[1] == 128

    @staticmethod
    def test_dataset_can_retrieve_sample(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether a sample can be retrieved from the dataset.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=128,
            input_height=128,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )

        sample = image_directory_dataset.get_sample(0)
        assert sample.index == 0
        assert len(sample.labels) == 1
        assert sample.labels[0].index == 0
        assert sample.labels[0].word_net_id == '00000000'
        assert sample.labels[0].name == 'Class 0'
        assert isinstance(sample.data, numpy.ndarray)
        assert sample.data.shape == (64, 64, 3)
        assert sample.data.dtype == numpy.uint8

    @staticmethod
    def test_dataset_can_retrieve_multiple_samples(image_directory_dataset_with_label_indices_path: str, label_map_file_path: str) -> None:
        """Tests whether multiple samples can be retrieved at the same time.

        Args:
            image_directory_dataset_with_label_indices_path (str): The path to the image directory dataset that is used for the tests.
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)
        image_directory_dataset = ImageDirectoryDataset(
            name="Test Dataset",
            path=image_directory_dataset_with_label_indices_path,
            label_index_regex=r'^.*/label-([0-9]+)/.*$',
            label_word_net_id_regex=None,
            input_width=128,
            input_height=128,
            down_sampling_method='none',
            up_sampling_method='none',
            label_map=label_map
        )

        samples = image_directory_dataset[2:6]
        assert isinstance(samples, list)
        assert len(samples) == 4

        samples = image_directory_dataset[[2, 10, 12, 20, 19]]
        assert isinstance(samples, list)
        assert len(samples) == 5

        samples = image_directory_dataset[(8, 13, 27)]
        assert isinstance(samples, list)
        assert len(samples) == 3

        samples = image_directory_dataset[numpy.array([21, 4])]
        assert isinstance(samples, list)
        assert len(samples) == 2

        samples = image_directory_dataset[range(10)]
        assert isinstance(samples, list)
        assert len(samples) == 10


class TestSample:
    """Represents the tests for the Sample class."""

    @staticmethod
    def test_sample_creation() -> None:
        """Tests whether a sample can be created."""

        image = numpy.random.randint(256, size=(32, 32, 3), dtype=numpy.uint8).astype(numpy.float64)
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert numpy.array_equal(sample.data, image)
        assert sample.labels == [label]

    @staticmethod
    def test_sample_creation_with_multiple_labels() -> None:
        """Tests whether a sample can be created with multiple labels."""

        image = numpy.random.randint(256, size=(32, 32, 3), dtype=numpy.uint8).astype(numpy.float64)
        label_0 = Label(0, '00000000', 'Class 0')
        label_1 = Label(1, '00000001', 'Class 1')
        sample = Sample(0, image.copy(), [label_0, label_1])
        assert sample.index == 0
        assert numpy.array_equal(sample.data, image)
        assert sample.labels == [label_0, label_1]

    @staticmethod
    def test_sample_creation_with_pytorch_image() -> None:
        """Tests whether a sample can be created with an image that has the PyTorch channel order."""

        image = numpy.random.randint(256, size=(3, 32, 64), dtype=numpy.uint8).astype(numpy.float64)
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert sample.data.shape[0] == 32
        assert sample.data.shape[1] == 64
        assert sample.data.shape[2] == 3
        assert numpy.array_equal(sample.data, numpy.moveaxis(image, [0, 1, 2], [2, 0, 1]))
        assert sample.labels == [label]

    @staticmethod
    def test_sample_creation_with_float_image() -> None:
        """Tests whether a sample can be created with an image that has the float data type and pixel values between 0.0 and 255.0. """

        image = numpy.random.randint(256, size=(32, 32, 3)).astype(dtype=numpy.float64)
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert numpy.array_equal(sample.data, image.astype(numpy.uint8))
        assert sample.labels == [label]

    @staticmethod
    def test_sample_creation_with_float_image_between_zero_and_one() -> None:
        """Tests whether a sample can be created with an image that has the float data type and pixel values between 0.0 and 1.0."""

        image = numpy.random.uniform(low=0.0, high=1.0, size=(32, 32, 3))
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert numpy.array_equal(sample.data, (image * 255.0).astype(numpy.uint8))
        assert sample.labels == [label]

    @staticmethod
    def test_sample_creation_with_float_image_between_negative_one_and_one() -> None:
        """Tests whether a sample can be created with an image that has the float data type and pixel values between -1.0 and 1.0."""

        image = numpy.random.uniform(low=-1.0, high=1.0, size=(32, 32, 3))
        label = Label(0, '00000000', 'Class 0')
        sample = Sample(0, image.copy(), label)
        assert sample.index == 0
        assert numpy.array_equal(sample.data, ((image + 1) * (255.0 / 2.0)).astype(numpy.uint8))
        assert sample.labels == [label]


class TestLabelMap:
    """Represents the tests for the LabelMap class."""

    @staticmethod
    def test_labels_can_be_retrieved_via_index(label_map_file_path: str) -> None:
        """Tests whether labels can be retrieved via index from a label map.

        Args:
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        assert label_map.get_label_name_from_index(0) == 'Class 0'
        assert label_map.get_label_name_from_index(1) == 'Class 1'
        assert label_map.get_label_name_from_index(2) == 'Class 2'

        with pytest.raises(LookupError):
            label_map.get_label_name_from_index(3)

    @staticmethod
    def test_labels_can_be_retrieved_via_wordnet_id(label_map_file_path: str) -> None:
        """Tests whether labels can be retrieved via WordNet ID from a label map.

        Args:
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        assert label_map.get_label_name_from_word_net_id('00000000') == 'Class 0'
        assert label_map.get_label_name_from_word_net_id('00000001') == 'Class 1'
        assert label_map.get_label_name_from_word_net_id('00000002') == 'Class 2'

        with pytest.raises(LookupError):
            label_map.get_label_name_from_word_net_id("")

    @staticmethod
    def test_labels_can_be_retrieved_via_one_hot_vector(label_map_file_path: str) -> None:
        """Tests whether labels can be retrieved via one-hot vector from a label map.

        Args:
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        assert label_map.get_label_names_from_n_hot_vector(numpy.array([1, 0, 0])) == ['Class 0']
        assert label_map.get_label_names_from_n_hot_vector(numpy.array([0, 1, 0])) == ['Class 1']
        assert label_map.get_label_names_from_n_hot_vector(numpy.array([0, 0, 1])) == ['Class 2']
        assert label_map.get_label_names_from_n_hot_vector(numpy.array([1, 0, 1])) == ['Class 0', 'Class 2']
        assert label_map.get_label_names_from_n_hot_vector(numpy.array([0, 1, 1])) == ['Class 1', 'Class 2']
        assert label_map.get_label_names_from_n_hot_vector(numpy.array([1, 1, 0])) == ['Class 0', 'Class 1']
        assert label_map.get_label_names_from_n_hot_vector(numpy.array([1, 1, 1])) == ['Class 0', 'Class 1', 'Class 2']

        with pytest.raises(LookupError):
            label_map.get_label_names_from_n_hot_vector(numpy.array([0, 0, 0, 1]))

    @staticmethod
    def test_labels_can_be_retrieved_via_generic_retrieval_method(label_map_file_path: str) -> None:
        """Tests whether labels can be retrieved via the general retrieval method of the label map class.

        Args:
            label_map_file_path (str): The path to the label map file that is used for the tests.
        """

        label_map = LabelMap(label_map_file_path)

        assert label_map.get_label_names(numpy.array([0])[0]) == 'Class 0'
        assert label_map.get_label_names(1) == 'Class 1'
        assert label_map.get_label_names('00000002') == 'Class 2'
        assert label_map.get_label_names(numpy.array([1, 1, 0])) == ['Class 0', 'Class 1']

        with pytest.raises(LookupError):
            label_map.get_label_names([0, 1])  # type: ignore
        with pytest.raises(LookupError):
            label_map.get_label_names((0, 1))  # type: ignore


class TestLabel:
    """Represents the tests for the Label class."""

    @staticmethod
    def test_label_creation() -> None:
        """Tests whether a label can be created."""

        label = Label(0, '00000000', 'Class 0')
        assert label.index == 0
        assert label.word_net_id == '00000000'
        assert label.name == 'Class 0'


class TestWorkspace:
    """Represents the tests for the Workspace class."""

    @staticmethod
    def test_workspace_creation() -> None:
        """Tests whether a workspace can be created."""

        workspace = Workspace()
        assert not workspace.is_closed
        assert len(workspace.projects) == 0

    @staticmethod
    def test_workspace_can_be_closed_multiple_times() -> None:
        """Tests whether a workspace can be closed multiple times without raising an error."""

        workspace = Workspace()
        workspace.close()
        workspace.close()

    @staticmethod
    def test_project_can_be_added_to_workspace(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether a project can be added to a workspace.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used in for the tests.
        """

        workspace = Workspace()
        workspace.add_project(project_file_with_hdf5_dataset_path)

        assert len(workspace.projects) == 1
        assert workspace.get_project_names() == ['Test Project']
        assert workspace.get_project('Test Project').name == 'Test Project'

    @staticmethod
    def test_multiple_projects_can_be_added_to_workspace(project_file_with_hdf5_dataset_path: str) -> None:
        """Tests whether multiple projects can be added to a workspace.

        Args:
            project_file_with_hdf5_dataset_path (str): The path to the project file that is used in for the tests.
        """

        workspace = Workspace()
        workspace.add_project(project_file_with_hdf5_dataset_path)
        workspace.projects[0].name = 'Test Project 1'
        workspace.add_project(project_file_with_hdf5_dataset_path)
        workspace.projects[1].name = 'Test Project 2'

        assert len(workspace.projects) == 2
        assert workspace.get_project_names() == ['Test Project 1', 'Test Project 2']
        assert workspace.get_project('Test Project 1').name == 'Test Project 1'
        assert workspace.get_project('Test Project 2').name == 'Test Project 2'

        workspace.close()
        for project in workspace.projects:
            assert project.is_closed

    @staticmethod
    def test_cannot_add_or_get_projects_of_closed_workspace() -> None:
        """Tests whether the workspace raises an error when adding or retrieving a project after the workspace was closed."""

        workspace = Workspace()
        workspace.close()

        with pytest.raises(ValueError):
            workspace.add_project('')

        with pytest.raises(ValueError):
            workspace.get_project('Test Project')

        with pytest.raises(ValueError):
            workspace.get_project_names()

    @staticmethod
    def test_workspace_cannot_find_unknown_project() -> None:
        """Tests whether a project can be added to a workspace."""

        workspace = Workspace()

        with pytest.raises(LookupError):
            workspace.get_project('Test Project')
