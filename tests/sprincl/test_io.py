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
def test_data_storage_at_functionality(storage, tmp_path, data, param_values):
    test_path = tmp_path / "test.file"
    with storage(test_path, mode='a') as data_storage:
        assert not data_storage._is_copy, 'Should not be a copy.'
        c = data_storage.at(data_key='param_values')
        assert c.data_key == 'param_values', "Data key was not changed."
        assert c._is_copy, 'Should be a copy, not all the mandatory parameters were set.'
        with pytest.raises(KeyError):
            # raises KeyError because the mandatory key was not set.
            data_storage.at(key='param_values')
        with pytest.raises(KeyError):
            # raises KeyError because non existing key was set.
            data_storage.at(data_key='param_values', key='key')
        with pytest.raises(TypeError):
            data_storage.at(data_key=1)

        data_storage.at(data_key='param_values').at(data_key='data')


@pytest.mark.parametrize("storage", [io.HDF5Storage, io.PickleStorage])
def test_data_storage(storage, tmp_path, data, param_values):
    # Test writing
    test_path = tmp_path / "test.file"
    data_storage = storage(test_path, mode='w')
    data_storage.at(data_key='data').write(data=data)
    data_storage.close()

    # Test reading
    data_storage = storage(test_path, mode='r')
    ret_data = data_storage.read()
    np.testing.assert_equal(ret_data, data)
    data_storage.close()

    # Test same with context manager
    with storage(test_path, mode='a') as data_storage:
        data_storage.at(data_key='param_values').write(data=param_values)

    with storage(test_path, mode='r') as data_storage:
        assert 'param_values' in data_storage
        assert 'data' in data_storage
        assert data_storage.at(data_key='param_values').exists()
        assert data_storage.at(data_key='data').exists()
        assert not data_storage.at(data_key='non_existing').exists()
        ret_param_values = data_storage['param_values']
        ret_param_values_2 = data_storage.at(data_key='param_values').read()
        with pytest.raises(io.NoDataSource):
            data_storage['non_existing']

    np.testing.assert_equal(ret_param_values, param_values)
    np.testing.assert_equal(ret_param_values_2, param_values)

    with storage(test_path, mode='a') as data_storage:
        data_storage.at(data_key='new_entry/data').write(data=data)
        assert data_storage.at(data_key='new_entry/data').exists()
        ret_data = data_storage.at(data_key='new_entry/data').read()
        np.testing.assert_equal(ret_data, data)


def test_no_storage(data):
    data_storage = io.NoStorage()
    with pytest.raises(io.NoDataSource):
        data_storage.read()
    with pytest.raises(io.NoDataTarget):
        data_storage.write(data)