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

from ome_seadragon.dataset import Dataset

logger = logging.getLogger(__name__)
MASK_FALSE = 0
MASK_TRUE = 255



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
    def cluster(self, shapes: List[Shape]) -> List[Shape]:
        ...


@dataclass
class DBScanClusterizer(Clusterizer):
    max_distance: float
    min_element: int = 1

    def cluster(self, shapes: List[Shape]) -> List[Shape]:
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
