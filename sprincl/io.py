"""'io module contains classes to load and dump different files like hdf5, etc.

"""

import copy
import pickle
from collections import OrderedDict
from abc import abstractmethod

import numpy as np
import h5py

from sprincl.tracker import MetaTracker
from sprincl.base import Param


class NoDataSource(Exception):
    """Raise when no data source available."""
    def __init__(self, message='No Data Source available.'):
        super().__init__(message)


class NoDataTarget(Exception):
    """Raise when no target source available."""
    def __init__(self):
        super().__init__('No Data Target available.')


class DataStorageBase(metaclass=MetaTracker.sub('MetaProcessor', Param, 'params')):
    """Implements a key, value storage object.

    """

    def __init__(self, **kwargs):
        for key, param in self.params.items():
            attr = kwargs.pop(key, param.default)
            if attr is not None and not isinstance(attr, param.dtype):
                raise TypeError('{} parameter is no subtype of {}.'.format(key, param.dtype))
            setattr(self, key, attr)
        if kwargs:
            key, _ = kwargs.popitem()
            raise TypeError('\'{}\' is an invalid keyword argument'.format(key))
        self._default_params = {key: param.default for key, param in self.params.items()}
        self._is_copy = False  # used in self.at and mandatory parameters.
        self.io = None

    @property
    def _mandatory_params(self):
        return set([key for key, param in self.params.items() if param.mandatory])

    @abstractmethod
    def read(self):
        """Should implement read functionality.

        """

    @abstractmethod
    def write(self, data):
        """Should implement write functionality.

        """

    def close(self):
        """Close opened io file object.

        """
        self.io.close()

    @abstractmethod
    def exists(self):
        """Return True if data exists.

        """
        raise NotImplementedError

    def keys(self):
        """Return keys of the io file object.

        """
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        self.io.close()

    def __contains__(self, key):
        return self.at(data_key=key).exists()

    def __getitem__(self, key):
        return self.at(data_key=key).read()

    def __setitem__(self, key, value):
        return self.at(data_key=key).write(value)

    def __bool__(self):
        return bool(self.io)

    def _update_defaults(self, kwargs):
        """Update and set kwargs as instance attributes. kwargs must have the same keys as self.params and values must
        have the same type as specified in self.params.

        """
        for key, value in kwargs.items():
            if key not in self.params.keys():
                raise KeyError('Non expected key: {}. Available keys: {}'.format(key, self.params.keys()))
            if not isinstance(value, self.params[key].dtype):
                raise TypeError('Value for key {} is of wrong type {}, whereas it should be of type {}.'.format(
                    key, type(value), self.params[key].dtype))
            setattr(self, key, value)

    def at(self, **kwargs):
        """Return a copy of the instance where kwargs become the attributes of the class.
        I.e. a specific self.data_key is set so that self.write(data) automatically writes the data to correct key.

        """
        missing_params = self._mandatory_params - set(kwargs.keys())
        if missing_params and not self._is_copy:
            raise KeyError('Missing mandatory parameters: {}'.format(missing_params))
        c = copy.copy(self)

        # pylint: disable=protected-access
        c._update_defaults(kwargs)
        c._is_copy = True
        return c


class NoStorage(DataStorageBase):
    def __bool__(self):
        return False

    def read(self):
        raise NoDataSource()

    def write(self, data):
        raise NoDataTarget()


class PickleStorage(DataStorageBase):
    """Experimental pickle storage that uses pickle to store data.

    """

    data_key = Param(str, 'data', mandatory=True)

    def __init__(self, path, mode='r', **kwargs):
        """
        Parameters
        ----------
        path: str
            Path to the pickled file.
        mode: str
            Write, Read or Append mode ['w', 'r', 'a'].

        """
        super().__init__(**kwargs)
        if mode not in ['w', 'r', 'a']:
            raise ValueError("Mode should be set to 'w', 'r' or 'a'.")
        self.io = open(path, mode + 'b')
        self.data = {}

    def _load_data(self):
        try:
            while True:
                dc = pickle.load(self.io)
                self.data.update({dc['key']: dc['data']})
        except EOFError:
            pass

    def read(self):
        """Return data for a given key. Need to load the complete pickle at first read. After the data is cached.

        Returns
        -------
        data for a given key

        """
        if not self.exists():
            raise NoDataSource("Key: '{}' does not exist.".format(self.data_key))
        return self.data[self.data_key]

    def write(self, data):
        """Write and pickle the data as: {"data": data, "key": key}

        Parameters
        ----------
        data: np.ndarray, dict
            Data being stored.

        """
        self.data[self.data_key] = data
        pickle.dump({"data": data, "key": self.data_key}, self.io)

    def keys(self):
        """Return keys from self.data. Need to load the complete pickle at first read.

        """
        if not self.data:
            self._load_data()
        return self.data.keys()

    def exists(self):
        """Return True if key exists in self.keys().

        """
        return self.data_key in self.keys()


class HDF5Storage(DataStorageBase):
    """HDF5 storage that stores data under different keys.

    """
    data_key = Param(str, 'data', mandatory=True)

    def __init__(self, path, mode='r', **kwargs):
        """
        Parameters
        ----------
        path: str
            Path to the hdf5 file.
        mode: str
            Write, Read or Append mode ['w', 'r', 'a'].

        """
        super().__init__(**kwargs)
        self.io = h5py.File(path, mode=mode)

    def read(self):
        """
        Returns
        -------
        data for a given key

        """
        if not self.exists():
            raise NoDataSource("Key: '{}' does not exist.".format(self.data_key))
        data = self.io[self.data_key]
        if isinstance(data, h5py.Group):
            # Change key to integer if k is digit, so that we can use the dict like a tuple or list
            return OrderedDict(((int(k) if k.isdigit() else k, v[()]) for k, v in data.items()))
        return data[()]

    def write(self, data):
        """
        Parameters
        ----------
        data: np.ndarray, dict
            Data being stored. Dictionaries are pickled and stored as strings.

        """
        if isinstance(data, dict):
            for key, value in data.items():
                shape, dtype = self._get_shape_dtype(value)
                self.io.require_dataset(data=value, shape=shape, dtype=dtype, name='{}/{}'.format(self.data_key, key))
        elif isinstance(data, tuple):
            for key, value in enumerate(data):
                shape, dtype = self._get_shape_dtype(value)
                self.io.require_dataset(data=value, shape=shape, dtype=dtype, name='{}/{}'.format(self.data_key, key))
        else:
            shape, dtype = self._get_shape_dtype(data)
            self.io.require_dataset(data=data, shape=shape, dtype=dtype, name=self.data_key)

    def exists(self):
        """Returns True if key exists in self.io.

        """
        return self.data_key in self.io

    def keys(self):
        """Return keys of the storage.

        """
        return self.io.keys()

    @staticmethod
    def _get_shape_dtype(value):
        """Infer shape and dtype of given element v.

        Parameters
        ----------
        value: np.ndarray, str, int, float
            Element for which we want to infer the shape and dtype.

        Returns
        -------
        shape, dtype: tuple, type
            Return the shape and dtype of v that works with h5py.require_dataset

        """
        if not isinstance(value, np.ndarray):
            shape = ()
            dtype = h5py.special_dtype(vlen=str) if isinstance(value, str) else np.dtype(type(value))
        else:
            shape = value.shape
            dtype = value.dtype
        return shape, dtype
