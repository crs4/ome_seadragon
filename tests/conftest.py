#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict

import numpy as np
import pytest

from ome_seadragon import Configuration
from ome_seadragon.dzi import DZIAdapterFactory, Palette


class TestConfiguration(Configuration):
    def __init__(self, conf: Dict):
        self.conf = conf

    def __getattr__(self, attr):
        try:
            return self.conf[attr]
        except KeyError:
            raise AttributeError(attr)


class TestPalette(Palette):
    def __call__(self, tile: np.ndarray) -> np.ndarray:
        shape = tile.shape
        colored_tile = np.array(
            list(map(lambda x: [int(x * 100)] * 4, np.nditer(tile)))
        )
        return colored_tile.reshape(shape + (4,))


@pytest.fixture
def conf():
    return TestConfiguration({"DEEPZOOM_TILE_SIZE": 2})


@pytest.fixture
def palette():
    return TestPalette()


@pytest.fixture
def dzi_adapter(backend, dataset, palette, conf):
    return DZIAdapterFactory(backend.upper(), palette, conf).get_adapter(dataset.path)
