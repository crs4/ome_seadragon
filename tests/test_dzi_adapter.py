import logging
import math
import os

import numpy as np
import pytest
import tiledb

from dzi_adapter.shapes import OpenCVShapeConverter, Shape, TileDBDataset

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def box_mask():
    """
    array([[50, 50,  0,  0,  0,  0,  0,  0,  0,  0],
           [50, 80, 80, 80, 80,  0,  0,  0,  0,  0],
           [ 0, 80, 80, 80, 80,  0,  0,  0,  0,  0],
           [ 0, 80, 80, 80, 80,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0, 90, 90,  0],
           [ 0,  0,  0,  0,  0,  0,  0, 90, 90,  0],
           [ 0,  0,  0,  0,  0,  0,  0, 90, 90,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]], dtype=uint8)
    """

    mask = np.zeros((10, 20), dtype="uint8")
    mask[:2, :2] = 50
    mask[1:4, 1:5] = 80
    mask[6:9, 7:9] = 90
    return mask


@pytest.fixture
def expected_shapes(threshold, tile_size, factor):
    """
    shapes according to box_mask
    """
    if threshold < 50:
        shapes = [
            ((0, 0), (1, 0), (4, 1), (1, 3), (0, 1), (2, 1), (1, 2), (4, 3)),
            ((7, 6), (8, 6), (8, 8), (7, 8)),
        ]
    elif threshold < 80:
        shapes = [
            ((1, 1), (4, 1), (4, 3), (1, 3)),
            ((7, 6), (8, 6), (8, 8), (7, 8)),
        ]
    elif threshold < 90:
        shapes = [
            ((7, 6), (8, 6), (8, 8), (7, 8)),
        ]
    else:
        shapes = []

    shapes = [
        Shape(tuple(map(tuple, np.array(s)))).rescale(tile_size * factor)
        for s in shapes
    ]
    return shapes


@pytest.fixture
def dataset(box_mask, backend, tmp_path, factor, tile_size):
    if backend == "tiledb":
        uri = os.path.join(tmp_path, "test.tiledb")
        tiledb.DenseArray.from_numpy(uri, box_mask)
        with tiledb.open(uri, mode="w") as array:
            original_height = box_mask.shape[1] * factor * tile_size
            original_width = box_mask.shape[0] * factor * tile_size

            array.meta["slide_path"] = os.path.join(tmp_path, "slide_path.ndpi")
            array.meta["original_height"] = original_height
            array.meta["original_width"] = original_width
            array.meta["tumor.tile_size"] = tile_size
            array.meta["tumor.rows"] = original_height / (factor * tile_size)
            array.meta["tumor.columns"] = original_width / (factor * tile_size)
            array.meta["tumor.dzi_sampling_level"] = math.ceil(
                math.log2(max(*[original_height / factor, original_width / factor]))
            )
        return TileDBDataset(array)


@pytest.fixture
def shape_converter(shape_converter_imp):
    if shape_converter_imp == "opencv":
        return OpenCVShapeConverter()


@pytest.mark.parametrize("backend", ["tiledb"])
@pytest.mark.parametrize("shape_converter_imp", ["opencv"])
@pytest.mark.parametrize("threshold", [0, 60, 85, 100])
@pytest.mark.parametrize("factor", [2])
@pytest.mark.parametrize("tile_size", [2])
def test_shape_converter(
    dataset, shape_converter, expected_shapes, threshold, tile_size, factor
):
    shapes = shape_converter.convert(dataset, threshold)
    assert {frozenset(s.points) for s in shapes} == {
        frozenset(s.points) for s in expected_shapes
    }
