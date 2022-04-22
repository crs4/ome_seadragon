from typing import Tuple

import numpy as np
import zarr

from ome_seadragon.dataset import Dataset, DatasetFactory, get_dzi_level


class GroupDataset(Dataset):
    def __init__(self, group: zarr.hierarchy.Group, array_name: str = None):
        self._group = group
        self._array = group[array_name] if array_name else list(group.arrays())[0][1]

    @property
    def shape(self) -> Tuple[int, int]:
        return self._array.shape

    @property
    def tile_size(self) -> Tuple[int, int]:
        return self._array.attrs["tile_size"]

    @property
    def dzi_sampling_level(self) -> int:
        return self._array.attrs["dzi_sampling_level"]

    @property
    def slide_path(self) -> str:
        return self._group.attrs["filename"]

    @property
    def slide_resolution(self) -> Tuple[int, int]:
        return self._group.attrs["resolution"]

    @property
    def array(self) -> np.ndarray:
        return np.array(self._array)


class ZarrDatasetFactory(DatasetFactory, default_name="zip"):
    def get(self, path):
        return GroupDataset(zarr.open(path))
