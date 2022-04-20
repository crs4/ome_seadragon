import abc
import os
from math import ceil, log2
from typing import Tuple

import numpy as np


class Dataset(abc.ABC):

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

    def zoom_factor(self):
        def _get_dzi_max_level(slide_res):
            return get_dzi_level(slide_res)

        dzi_max_level = _get_dzi_max_level(self.slide_resolution)
        level_diff = dzi_max_level - self.dzi_sampling_level
        tile_level = log2(self.tile_size)
        return 2 ** (level_diff + tile_level)


def get_dzi_level(shape):
    return int(ceil(log2(max(*shape))))


class DatasetFactory:
    _registry = {}
    def __init_subclass__(cls, /, default_name, **kwargs):
        cls._registry[default_name] = cls

    def get(self, path: str):
        try:
            ext = os.path.splitext(path)[1][1:]
        except KeyError:
            raise UnsupportedDataset(path)
        return self._registry[ext]().get(path)



class UnsupportedDataset(Exception):
    pass
