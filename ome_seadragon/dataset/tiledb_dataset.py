from math import ceil, log2
from typing import Tuple

import numpy as np
import tiledb

from ome_seadragon.dataset import Dataset


class TileDBDataset(Dataset):
    def __init__(self, array: tiledb.Array):
        self._array = tiledb.open(array.uri, mode="r")

    @property
    def path(self):
        return self._array.uri

    @property
    def shape(self):
        return self._array.shape

    @property
    def tile_size(self) -> Tuple[int, int]:
        return self._array.meta["tumor.tile_size"]

    @property
    def dzi_sampling_level(self) -> int:
        return self._array.meta["tumor.dzi_sampling_level"]

    @property
    def slide_path(self) -> str:
        return self._array.meta["slide_path"]

    @property
    def slide_resolution(self) -> Tuple[int, int]:
        return (self._array.meta["original_width"], self._array.meta["original_height"])

    @property
    def array(self) -> np.ndarray:
        return np.array(self._array)

    def zoom_factor(self):
        def _get_dzi_level(shape):
            return int(ceil(log2(max(*shape))))

        def _get_dzi_max_level(slide_res):
            return _get_dzi_level(slide_res)

        dzi_max_level = _get_dzi_max_level(self.slide_resolution)
        level_diff = dzi_max_level - self.dzi_sampling_level
        tile_level = log2(self.tile_size)
        return 2 ** (level_diff + tile_level)


def get_dataset(path: str)->TileDBDataset:
    return TileDBDataset(tiledb.open(path))
