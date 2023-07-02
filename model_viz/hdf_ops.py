import h5py
from dataclasses import dataclass
from typing import List, Iterator
import numpy as np


@dataclass
class HDFReader:
    """Class for creating HDF5 reader"""

    name: str
    path: str
    mode: str = "r"

    def __post_init__(self):
        self.hdf = h5py.File(self.path, self.mode)
        self.__data = self.hdf

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"HDFReader(name={self.name}, path={self.path}, mode={self.mode})"

    def __del__(self):
        self.hdf.close()

    def get_data(self, group, stock) -> np.ndarray:
        """Returns stock data as numpy array"""
        return self.__data[f"{group}/{stock}"]

    def get_stock(self, stock) -> np.ndarray:
        """Returns stock data as numpy array"""
        return self.get_data("stocks", stock)

    def get_stock_with_empirical_data(self, stock) -> np.ndarray:
        """Returns stock data with empirical data as numpy array"""
        return self.get_data("stocks_with_empirical_data", stock)

    def get_empirical_data(self) -> List[np.ndarray]:
        """Returns empirical data as list of numpy arrays"""
        empirical_data = []
        for data in self.__data["empirical_data"].keys():
            empirical_data.append(self.__data[f"empirical_data/{data}"])
        return empirical_data

    def get_iterator(self, group) -> Iterator[np.ndarray]:
        """Iterates over stocks"""
        for stock in self.__data[group].keys():
            yield self.get_data(group, stock)
