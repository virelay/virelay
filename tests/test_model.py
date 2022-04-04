"""Contains the tests for the model abstractions of ViRelAy"""

import pathlib

import numpy
import pytest

from virelay.model import LabelMap


@pytest.fixture(scope='function')
def label_map_file_path(tmp_path: pathlib.Path) -> str:
    """A test fixture, which creates a label map file.

    Parameters
    ----------
        tmp_path: pathlib.Path
            The path to a temporary directory. This a an automatically created temporary path andcomes from the build in
            tmp_path fixture of PyTest.

    Returns
    -------
        str
            Returns the path to the created label map file.
    """

    label_map_file_path = tmp_path / 'label-map.json'
    label_map_file_path.write_text(
        '[{"index": 0, "word_net_id": "00000000", "name": "Class 0"},'
        '{"index": 1, "word_net_id": "00000001", "name": "Class 1"},'
        '{"index": 2, "word_net_id": "00000002", "name": "Class 2"}]'
    )
    return label_map_file_path.as_posix()


class TestLabelMap:
    """Represents the tests for the LabelMap class."""

    @staticmethod
    def test_label_map(label_map_file_path: str) -> None:
        """Tests the label map.

        Parameters
        ----------
            label_map_file_path: str
                The path to the label map file that is used for the tests.
        """

        # Loads the label map file
        label_map = LabelMap(label_map_file_path)

        # Checks if labels can be retrieved via index
        assert label_map.get_label_from_index(0) == 'Class 0'
        with pytest.raises(LookupError):
            label_map.get_label_from_index(3)

        # Checks if labels can be retrieved via WordNet IDs
        assert label_map.get_label_from_word_net_id('00000001') == 'Class 1'
        with pytest.raises(LookupError):
            label_map.get_label_from_word_net_id("")
        with pytest.raises(LookupError):
            label_map.get_labels_from_n_hot_vector(numpy.array([0, 0, 0, 1]))

        # Checks if labels can be retrieved via one-hot encoded vectors
        assert label_map.get_labels_from_n_hot_vector(numpy.array([1, 0, 1])) == ['Class 0', 'Class 2']

        # Checks whether the generic label retrieval method supports all formats
        assert label_map.get_labels(numpy.array([0])[0]) == 'Class 0'
        assert label_map.get_labels(1) == 'Class 1'
        assert label_map.get_labels('00000002') == 'Class 2'
        assert label_map.get_labels(numpy.array([1, 1, 0])) == ['Class 0', 'Class 1']
        with pytest.raises(LookupError):
            label_map.get_labels([])
