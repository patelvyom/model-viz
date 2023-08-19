import h5py
from dataclasses import dataclass


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

    def __repr__(self):
        return f"HDFReader(name={self.name}, path={self.path}, mode={self.mode})"

    def __del__(self):
        self.hdf.close()

    def _get_group_items(self, group) -> list[h5py.Group]:
        """Iterates over items in a group"""
        return [self.__data[f"{group}/{item}"] for item in self.__data[group]]

    def get_all_groups(self) -> dict[str, list[h5py.Group]]:
        """
        Return iterators of "plotting_groups" for all groups
        """
        groups = {}
        for group in self.__data:
            groups[group] = self._get_group_items(group)

        return groups

    def get_group(self, root_group: str, sub_group: list[str]):
        """
        Return group at the lowest level of hierarchy (determined by last element of `sub_group`)

        Args:
            root_group: Root group to start searching from
            sub_group: List of groups to traverse
        """
        group = self.__data[root_group]
        sub_group = group.get("/".join(sub_group), None)
        if sub_group is None:
            raise ValueError(f"Group {sub_group} not found in {root_group}")
        return sub_group
