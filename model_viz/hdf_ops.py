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
        self.data = self.hdf[self.name]

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"HDFReader(name={self.name}, path={self.path}, mode={self.mode})"

    def __del__(self):
        self.hdf.close()

    def get_stock(self, stock) -> np.ndarray:
        """Returns stock data as numpy array"""
        return self.data["stocks"][stock][:]

    def get_stock_names(self) -> List[str]:
        """Returns list of stock names"""
        return self.data["stocks"].keys()

    def stock_iterator(self) -> Iterator[np.ndarray]:
        """Iterates over stocks"""
        for stock in self.data["stocks"].keys():
            yield self.get_stock(stock)
