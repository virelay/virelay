import pytest
import numpy as np

from sprincl import io


@pytest.fixture
def data():
    return np.random.rand(10, 2)


@pytest.fixture
def param_values():
    return dict(param1=1, param2='string')


@pytest.mark.parametrize("storage", [io.HDF5Storage, io.PickleStorage])
def test_data_storage(storage, tmp_path, data, param_values):
    # Test writing
    test_path = tmp_path / "test.file"
    data_storage = storage(test_path, mode='w')
    data_storage.write(key='data', data=data)
    data_storage.close()

    # Test reading
    data_storage = storage(test_path, mode='r')
    ret_data = data_storage.read('data')
    np.testing.assert_equal(ret_data, data)
    data_storage.close()

    # Test same with context manager
    with storage(test_path, mode='a') as data_storage:
        data_storage.write(key='param_values', data=param_values)

    with storage(test_path, mode='r') as data_storage:
        assert 'param_values' in data_storage
        assert 'data' in data_storage
        ret_param_values = data_storage['param_values']
        with pytest.raises(KeyError):
            data_storage['non_existing']

    np.testing.assert_equal(ret_param_values, param_values)
