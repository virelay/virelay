import pickle
from abc import ABCMeta, abstractmethod

import h5py


class DataStorageBase(metaclass=ABCMeta):
    """Implements a key, value storage object.

    """

    @abstractmethod
    def read(self, key): pass

    @abstractmethod
    def write(self, key, data): pass

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
        return self.write(key, value)


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

    def write(self, key, data):
        """Write and pickle the data as: {"data": data, "key": key}

        Parameters
        ----------
        key: str
            With which key the data is being stored.
        data: np.ndarray, dict
            Data being stored.

        """
        pickle.dump({"data": data, "key": key}, self.io)

    def keys(self):
        """Return keys from self.data. Need to load the complete pickle at first read.

        """
        if not self.data:
            self._load_data()
        return self.data.keys()

    def exists(self, key):
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
        self.io = h5py.File(path, mode=mode, **kwargs)

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
        data = self.io[key][()]
        if isinstance(data, str):
            data = pickle.loads(data.encode())
        return data

    def write(self, key, data):
        """
        Parameters
        ----------
        key: str
            At which key value the data is being stored.
        data: np.ndarray, dict
            Data being stored. Dictionaries are pickled and stored as strings.

        """
        if isinstance(data, dict):
            data = pickle.dumps(data, 0).decode()
        self.io.create_dataset(data=data, name=key)

    def exists(self, key):
        """Returns True if key exists in self.io.

        """
        return key in self.io

    def keys(self):
        """Return keys of the storage.

        """
        return self.io.keys()
