from typing import Tuple

import numpy as np
import tiledb

from ome_seadragon.dataset import Dataset, DatasetFactory


class TileDBDataset(Dataset):
    def __init__(self, array: tiledb.Array):
        self._array = tiledb.open(array.uri, mode="r")


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



class TiledbDatasetFactory(DatasetFactory, default_name="tiledb"):
    def get(self, path):
        return TileDBDataset(tiledb.open(path))
        
