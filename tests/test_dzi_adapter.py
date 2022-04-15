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

from ome_seadragon.dataset.tiledb_dataset import TileDBDataset
from ome_seadragon.dzi import Palette, get_dzi_level
from ome_seadragon.shapes import OpenCVShapeConverter, Shape, shapes_to_json

django_settings.configure(
    STATIC_URL="", ROOT_URLCONF="ome_seadragon.urls", DEBUG=True, ALLOWED_HOSTS=["*"]
)
#  os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
import django

django.setup()


@pytest.fixture(params=[(10, 20)])
def box_mask(request):
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

    shape = request.param
    mask = np.zeros(shape, dtype="uint8")
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
        rows = tiledb.Dim(
            name="rows",
            domain=(0, box_mask.shape[0] - 1),
            tile=tile_size,
            dtype=np.uint16,
        )
        columns = tiledb.Dim(
            name="columns",
            domain=(0, box_mask.shape[1] - 1),
            tile=tile_size,
            dtype=np.uint16,
        )
        domain = tiledb.Domain(rows, columns)
        attributes = [tiledb.Attr("tumor", dtype="uint8")]
        schema = tiledb.ArraySchema(domain=domain, sparse=False, attrs=attributes)
        tiledb.DenseArray.create(uri, schema)
        #  tiledb.DenseArray.from_numpy(uri, box_mask)
        with tiledb.open(uri, mode="w") as array:
            array[:] = {"tumor": box_mask}
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
        assert (np.array(tiledb.open(uri, mode="r")) == box_mask).all()
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
@pytest.mark.parametrize("threshold", [1, 60, 85, 100])
@pytest.mark.parametrize("factor", [2])
@pytest.mark.parametrize("tile_size", [2])
@pytest.mark.skip("to be updated")
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


@pytest.mark.parametrize("factor", [2])
@pytest.mark.parametrize("tile_size", [2])
@pytest.mark.parametrize("backend", ["tiledb"])
@pytest.mark.parametrize("box_mask", [(10, 20)], indirect=True)
def test_dzi_adapter_get_description(dzi_adapter, box_mask, tile_size, factor):
    dzi_description = dzi_adapter.get_dzi_description()
    width = box_mask.shape[0] * factor * tile_size
    height = box_mask.shape[1] * factor * tile_size
    expected_dzi_description = (
        f'<Image xmlns="http://schemas.microsoft.com/deepzoom/2008"'
        + f' Format="png" Overlap="0" TileSize="{tile_size}"><Size Height="{height}" Width="{width}"/></Image>'
    )
    assert dzi_description == expected_dzi_description


def tile_output_mapping():
    param_output_mapping = {
        (1, 1, 0, 0, 1): np.array(
            [
                [50]*4,
                [50]*4,
                [50]*4,
                [80]*4,
            ]
        )
    }
    res = [tuple(k) + tuple([v]) for k, v in param_output_mapping.items()]
    return res


@pytest.mark.parametrize(
    "factor, tile_size, row, column, threshold, expected_output", tile_output_mapping()
)
@pytest.mark.parametrize("backend,", ["tiledb"])
@pytest.mark.parametrize("box_mask", [(256, 256)], indirect=True)
def test_dzi_adapter_get_tile(
    box_mask, factor, dzi_adapter, row, column, threshold, tile_size, expected_output
):
    dzi_max_level = get_dzi_level(np.array(box_mask.shape) * factor * tile_size)
    level = dzi_max_level - (factor * tile_size - 1)
    tile = dzi_adapter.get_tile(
        level,
        row,
        column,
        threshold=threshold / 100,
    )
    tile_array = np.array(tile.getdata())
    assert (tile_array == expected_output).all()
