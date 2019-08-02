import copy
import pickle
from abc import ABCMeta, abstractmethod

import numpy as np
import h5py


def automatic_key(func):
    """This wrapper automatically uses self.key is key is not provided.
    Use to decorate a class method.

    """
    def func_wrapper(self, key=None):
        key = key or self.key
        return func(self, key)
    return func_wrapper


class DataStorageBase(metaclass=ABCMeta):
    """Implements a key, value storage object.

    """

    def __init__(self):
        self.key = 'data'

    @abstractmethod
    def read(self, key):
        pass

    @abstractmethod
    def write(self, data):
        pass

    def close(self):
        self.io.close()

    def exists(self, key):
        raise NotImplementedError

    def keys(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.io.close()

    def __contains__(self, key):
        return self.exists(key)

    def __getitem__(self, key):
        return self.read(key)

    def __setitem__(self, key, value):
        self.key = key
        return self.write(value)

    def at(self, key):
        """Return a copy of the instance with a self.key=key
        In this way self.write(data) automatically writes the data to self.key

        Parameters
        ----------
        key: str
            At which key the data will be stored.

        """
        c = copy.copy(self)
        c.key = key
        return c


class PickleStorage(DataStorageBase):
    def __init__(self, path, mode='r'):
        """
        Parameters
        ----------
        path: str
            Path to the pickled file.
        mode: str
            Write, Read or Append mode ['w', 'r', 'a'].

        """
        super().__init__()
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

    @automatic_key
    def read(self, key):
        """Return data for a given key. Need to load the complete pickle at first read. After the data is cached.

        Parameters
        ----------
        key: str
            Key of the data stored in self.io

        Returns
        -------
        data for a given key

        """

        if not self.data:
            self._load_data()
        return self.data[key]

    def write(self, data):
        """Write and pickle the data as: {"data": data, "key": key}

        Parameters
        ----------
        data: np.ndarray, dict
            Data being stored.

        """
        self.data[self.key] = data
        pickle.dump({"data": data, "key": self.key}, self.io)

    def keys(self):
        """Return keys from self.data. Need to load the complete pickle at first read.

        """
        if not self.data:
            self._load_data()
        return self.data.keys()

    @automatic_key
    def exists(self, key=None):
        """Return True if key exists in self.keys().

        """
        return key in self.keys()


class HDF5Storage(DataStorageBase):
    def __init__(self, path, mode='r', **kwargs):
        """
        Parameters
        ----------
        path: str
            Path to the hdf5 file.
        mode: str
            Write, Read or Append mode ['w', 'r', 'a'].

        """
        super().__init__()
        self.io = h5py.File(path, mode=mode, **kwargs)

    @automatic_key
    def read(self, key):
        """
        Parameters
        ----------
        key: str
            Key of the data stored in self.io

        Returns
        -------
        data for a given key

        """
        data = self.io[key]
        if isinstance(data, h5py.Group):
            # Change key to integer if k is digit, so that we can use the dict like a tuple or list
            return dict(((int(k) if k.isdigit() else k, v[()]) for k, v in data.items()))
        else:
            return data[()]

    def write(self, data):
        """
        Parameters
        ----------
        data: np.ndarray, dict
            Data being stored. Dictionaries are pickled and stored as strings.

        """
        if isinstance(data, dict):
            for k, v in data.items():
                shape, dtype = self._get_shape_dtype(v)
                self.io.require_dataset(data=v, shape=shape, dtype=dtype, name='{}/{}'.format(self.key, k))
        elif isinstance(data, tuple):
            for k, v in enumerate(data):
                shape, dtype = self._get_shape_dtype(v)
                self.io.require_dataset(data=v, shape=shape, dtype=dtype, name='{}/{}'.format(self.key, k))
        else:
            shape, dtype = self._get_shape_dtype(data)
            self.io.require_dataset(data=data, shape=shape, dtype=dtype, name=self.key)

    @automatic_key
    def exists(self, key):
        """Returns True if key exists in self.io.

        """
        return key in self.io

    def keys(self):
        """Return keys of the storage.

        """
        return self.io.keys()

    @staticmethod
    def _get_shape_dtype(v):
        """Infer shape and dtype of given element v.

        Parameters
        ----------
        v: np.ndarray, str, int, float
            Element for which we want to infer the shape and dtype.

        Returns
        -------
        shape, dtype: tuple, type
            Return the shape and dtype of v that works with h5py.require_dataset

        """
        if not isinstance(v, np.ndarray):
            shape = ()
            dtype = h5py.special_dtype(vlen=str) if isinstance(v, str) else np.dtype(type(v))
        else:
            shape = v.shape
            dtype = v.dtype
        return shape, dtype
