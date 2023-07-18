import h5py
from dataclasses import dataclass
from typing import List, Iterator, Dict
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
        return self.__data[key]

    def __len__(self):
        return len(self.__data)

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

    def _get_iterator(self, group) -> Iterator[h5py.Group]:
        """Iterates over stocks"""
        for stock in self.__data[group].keys():
            yield self.get_data(group, stock)

    def get_group_iterators(self) -> dict[str, Iterator[h5py.Group]]:
        """
        Return iterators of "plotting_groups" for all groups
        """
        groups = {}
        for group in self.__data:
            groups[group.title()] = self._get_iterator(group)

        return groups
