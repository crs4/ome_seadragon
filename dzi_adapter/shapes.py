#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import logging
import os
from dataclasses import dataclass
from typing import List, Tuple, Union

import cv2
import numpy as np
import tiledb

logger = logging.getLogger(__name__)
MASK_FALSE = 0
MASK_TRUE = 255


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

    @property
    def array(self) -> np.ndarray:
        return np.array(self._array)


def get_dataset(path):
    ext = os.path.splitext(path)[1]
    if ext == ".tiledb":
        return TileDBDataset(tiledb.open(path))
    else:
        raise UnsupportedDataset(path)


class UnsupportedDataset(Exception):
    pass


Coord = Union[int, float]
Point = Tuple[Coord, Coord]


@dataclass(frozen=True)
class Shape:
    points: Tuple[Point]

    def rescale(self, factor: float) -> "Shape":
        return Shape(tuple(map(tuple, np.array(self.points) * factor)))

    def __eq__(self, other):
        return set(self.points) == set(other.points)

    def as_points(self) -> List:
        points = [{"point": {"x": p[0], "y": p[1]}} for p in self.points]
        return points


def shapes_to_json(shapes: List[Shape]) -> str:
    return json.dumps({"shapes": shapes}, default=lambda s: s.as_points())


class ShapeConverter(abc.ABC):
    @abc.abstractmethod
    def convert(self, dataset: Dataset, threshold: float) -> List[Shape]:
        ...


class OpenCVShapeConverter(ShapeConverter):
    def convert(self, dataset: Dataset, threshold: float) -> List[Shape]:
        mask = dataset.array
        mask[mask < threshold] = MASK_FALSE
        mask[mask >= threshold] = MASK_TRUE

        contours, _ = cv2.findContours(
            mask, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE
        )
        factor = dataset.slide_resolution[0] / dataset.shape[0]
        points = [tuple(map(tuple, np.squeeze(c))) for c in contours if c.size >= 3]
        points = [p + (p[0],) for p in points]
        shapes = [Shape(point).rescale(factor) for point in points]
        return shapes


def get_shape_converter(cls: str):
    if cls == "opencv":
        return OpenCVShapeConverter()
    else:
        raise KeyError(f"shape converter {cls} does not exist")
