import json
import math
import os
from pathlib import Path
from typing import List, Tuple
from unittest.mock import patch

import numpy as np
import pytest
import tiledb
from django.conf import settings as django_settings
from django.test import Client

from ome_seadragon.dzi_adapter.shapes import (
    OpenCVShapeConverter,
    Shape,
    TileDBDataset,
    shapes_to_json,
)

django_settings.configure(
    STATIC_URL="", ROOT_URLCONF="ome_seadragon.urls", DEBUG=True, ALLOWED_HOSTS=["*"]
)
#  os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
import django

django.setup()


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
            [(7.0, 6.0), (7.0, 8.0), (8.0, 8.0), (8.0, 6.0), (7.0, 6.0)],
            [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 2.0),
                (1.0, 3.0),
                (4.0, 3.0),
                (4.0, 1.0),
                (2.0, 1.0),
                (1.0, 0.0),
                (0.0, 0.0),
            ],
        ]

    elif threshold < 80:
        shapes = [
            ((7.0, 6.0), (7.0, 8.0), (8.0, 8.0), (8.0, 6.0), (7.0, 6.0)),
            ((1.0, 1.0), (1.0, 3.0), (4.0, 3.0), (4.0, 1.0), (1.0, 1.0)),
        ]

    elif threshold < 90:
        shapes = [((7.0, 6.0), (7.0, 8.0), (8.0, 8.0), (8.0, 6.0), (7.0, 6.0))]
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


@pytest.fixture
def shape(points: List[Tuple[int, int]]):
    return Shape(points)


@pytest.fixture
def expected_json(points: List[Tuple[int, int]]):
    return [{"point": {"x": p[0], "y": p[1]}} for p in points]


@pytest.mark.parametrize("backend", ["tiledb"])
@pytest.mark.parametrize("shape_converter_imp", ["opencv"])
@pytest.mark.parametrize("threshold", [0, 60, 85, 100])
@pytest.mark.parametrize("factor", [2])
@pytest.mark.parametrize("tile_size", [2])
def test_shape_converter(
    dataset, shape_converter, expected_shapes, threshold, tile_size, factor
):
    shapes = shape_converter.convert(dataset, threshold)
    assert {s.points for s in shapes} == {s.points for s in expected_shapes}


from ome_seadragon import views
@pytest.mark.parametrize("dataset_id", [1])
@pytest.mark.parametrize("backend", ["tiledb"])
@pytest.mark.parametrize("threshold", [0])
@pytest.mark.parametrize("factor", [2])
@pytest.mark.parametrize("tile_size", [2])
@patch("ome_seadragon.views.get_original_file_by_id")
@patch.object(
    views,
    "settings",
)
def test_get_array_dataset_shapes(
    mock_settings,
    mock_get_original_file_by_id,
    dataset_id,
    dataset,
    threshold,
    tmp_path,
):
    mock_get_original_file_by_id.return_value.name = "test.tiledb"
    mock_settings.DATASETS_REPOSITORY = tmp_path

    client = Client()
    resp = client.get(f"/arrays/shapes/get/{dataset_id}/")

    print(resp)
    shapes = resp.json()
    assert isinstance(shapes, dict)
    assert list(shapes.keys()) == ["shapes"]
    assert len(shapes["shapes"]) == 2

    shape = shapes["shapes"][0]
    assert len(shape) > 0
    assert list(shape[0].keys()) == ["point"]
    assert list(shape[0].keys()) == ["point"]

    point = shape[0]["point"]
    assert len(point) > 0
    assert set(point.keys()) == {"x", "y"}


@pytest.mark.parametrize("points", [[(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]])
def test_shapes_to_json(shape, expected_json):
    res = shapes_to_json([shape, shape])
    assert res == json.dumps({"shapes": [expected_json, expected_json]})
