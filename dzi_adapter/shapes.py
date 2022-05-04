#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import logging
import os
from dataclasses import dataclass
from math import ceil, log2
from typing import List, Tuple, Union

import cv2
import geopandas as gpd
import numpy as np
import pandas as pd
import tiledb
from shapely.geometry import MultiPolygon, Polygon, box
from sklearn.cluster import DBSCAN

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

    @abc.abstractmethod
    def zoom_factor(self):
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

    def zoom_factor(self):
        def _get_dzi_level(shape):
            return int(ceil(log2(max(*shape))))

        def _get_dzi_max_level(slide_res):
            return _get_dzi_level(slide_res)

        dzi_max_level = _get_dzi_max_level(self.slide_resolution)
        level_diff = dzi_max_level - self.dzi_sampling_level
        tile_level = log2(self.tile_size)
        return 2 ** (level_diff + tile_level)


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

    @property
    def area(self):
        polygon = Polygon(self.points)
        return polygon.area


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
        factor = dataset.zoom_factor()
        logger.info("shape conversion with factor %s", factor)

        bounding_boxes = []
        for contour in contours:
            tmp_polygon = cv2.approxPolyDP(contour, 0.1, True)
            bounding_boxes.append(cv2.boundingRect(tmp_polygon))

        points = list(
            map(
                lambda b: (
                    (b[0], b[1]),
                    (b[0] + b[2], b[1]),
                    (b[0] + b[2], b[1] + b[3]),
                    (b[0], b[1] + b[3]),
                ),
                bounding_boxes,
            )
        )
        points = [p + (p[0],) for p in points]
        shapes = [Shape(point).rescale(factor) for point in points]
        return shapes


def get_shape_converter(cls: str):
    if cls == "opencv":
        return OpenCVShapeConverter()
    else:
        raise KeyError(f"shape converter {cls} does not exist")


class Clusterizer(abc.ABC):
    @abc.abstractmethod
    def cluster(self, shapes: List[Shape])->List[Shape]:
        ...


@dataclass
class DBScanClusterizer(Clusterizer):
    max_distance: float
    min_element: int = 1

    def cluster(self, shapes: List[Shape])->List[Shape]:
        df = gpd.GeoDataFrame(geometry=[Polygon(s.points) for s in shapes])
        df["x"] = df["geometry"].centroid.x
        df["y"] = df["geometry"].centroid.y
        coords = df[["x", "y"]].to_numpy()

        dbscan = DBSCAN(eps=self.max_distance, min_samples=self.min_element)
        clusters = dbscan.fit(coords)

        labels = pd.Series(clusters.labels_).rename("cluster")
        df = pd.concat([df, labels], axis=1)
        logger.info(df)

        clusters = []
        for cluster in df.groupby("cluster"):
            clusters.append(MultiPolygon(list(cluster[1]["geometry"])))

        cluster_shapes = [Shape(box(*c.bounds).exterior.coords) for c in clusters]
        return cluster_shapes

