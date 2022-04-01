#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import logging
from dataclasses import dataclass
from functools import cached_property
from typing import List, Tuple, Union

import cv2
import numpy as np
import tiledb


logger = logging.getLogger(__name__)


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

    @cached_property
    def array(self) -> np.ndarray:
        return np.array(self._array)


Coord = Union[int, float]
Point = Tuple[Coord, Coord]


@dataclass(frozen=True)
class Shape:
    points: Tuple[Point]

    def rescale(self, factor: float) -> "Shape":
        return Shape(tuple(map(tuple, np.array(self.points) * factor)))

    def __eq__(self, other):
        return set(self.points) == set(other.points)


class ShapeConverter(abc.ABC):
    @abc.abstractmethod
    def convert(self, dataset: Dataset, threshold: float) -> List[Shape]:
        ...


class OpenCVShapeConverter(ShapeConverter):
    def convert(self, dataset: Dataset, threshold: float) -> List[Shape]:
        mask = dataset.array
        mask[mask <= threshold] = 0
        mask[mask > threshold] = 255

        contours, _ = cv2.findContours(
            mask, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE
        )
        logger.debug("contours %s", contours)
        factor = dataset.slide_resolution[0] / dataset.shape[0]
        shapes = [
            Shape(tuple(map(tuple, np.squeeze(c)))).rescale(factor) for c in contours
        ]
        return shapes
