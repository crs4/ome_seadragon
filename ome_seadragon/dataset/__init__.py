import abc
import os
from typing import Tuple

import numpy as np


class Dataset(abc.ABC):
    @property
    @abc.abstractmethod
    def path(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def shape(self) -> Tuple[int, int]:
        ...

    @property
    @abc.abstractmethod
    def tile_size(self) -> Tuple[int, int]:
        ...

    @property
    @abc.abstractmethod
    def dzi_sampling_level(self) -> int:
        ...

    @property
    @abc.abstractmethod
    def slide_path(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def slide_resolution(self) -> Tuple[int, int]:
        ...

    @property
    @abc.abstractmethod
    def array(self) -> np.ndarray:
        ...

    @abc.abstractmethod
    def zoom_factor(self):
        ...


def get_dataset(path):
    ext = os.path.splitext(path)[1]
    from ome_seadragon.dataset.tiledb_dataset import get_dataset as get_tiledb_dataset
    if ext == ".tiledb":
        return get_tiledb_dataset(path)
    else:
        raise UnsupportedDataset(path)

class UnsupportedDataset(Exception):
    pass


