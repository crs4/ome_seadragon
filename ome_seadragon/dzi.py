import abc
import logging
from copy import copy
from math import ceil, log2, pow

import numpy as np
import palettable.colorbrewer.sequential as palettes
from lxml import etree
from PIL import Image

from ome_seadragon import Configuration
from ome_seadragon.dataset import Dataset, DatasetFactory
from ome_seadragon.errors import InvalidColorPalette, UnknownDZIAdaperType

logger = logging.getLogger(__name__)


def get_dzi_level(shape):
    return int(ceil(log2(max(*shape))))


class DZIAdapter(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def get_dzi_description(self):
        pass

    @abc.abstractmethod
    def get_tile(self, level, column, row, attribute_label=None, tile_size=None):
        pass


class HeatmapDZIAdapter(DZIAdapter):
    def __init__(
        self, dataset: Dataset, palette: "Palette", conf: Configuration = None
    ):
        super().__init__()
        self.dataset = dataset
        self.palette = palette
        self.conf = conf or Configuration()
        self.logger.debug("basic adapter initialized")

    def _get_dzi_tile_coordinates(self, row, column, tile_size, level):
        level_dimensions = self._get_dzi_level_dimensions(level)
        self.logger.debug(f"### DZI DIMENSIONS FOR LEVEL {level}: {level_dimensions}")
        x_min = row * tile_size
        y_min = column * tile_size
        x_max = x_min + tile_size
        y_max = y_min + tile_size
        return {
            "x_min": x_min,
            "x_max": min(x_max, level_dimensions["width"]),
            "y_min": y_min,
            "y_max": min(y_max, level_dimensions["height"]),
        }

    def _get_dzi_max_level(self):
        original_dimensions = self.dataset.slide_resolution
        return get_dzi_level((original_dimensions[0], original_dimensions[1]))

    def _get_dzi_level_dimensions(self, level):
        original_dimensions = self.dataset.slide_resolution
        max_dzi_level = self._get_dzi_max_level()
        scale_factor = pow(2, max_dzi_level - level)
        return {
            "width": original_dimensions[0] // scale_factor,
            "height": original_dimensions[1] // scale_factor,
        }

    def _get_dataset_dzi_dimensions(self):
        slide_resolution = self.dataset.slide_resolution
        return {"width": slide_resolution[0], "height": slide_resolution[1]}

    def _get_zoom_scale_factor(self, dzi_zoom_level):
        tiledb_zoom_level = self.dataset.dzi_sampling_level
        return pow(2, (tiledb_zoom_level - dzi_zoom_level))

    def _get_dataset_tile_coordinates(self, dzi_coordinates, zoom_scale_factor):
        return {k: (v * zoom_scale_factor) for (k, v) in dzi_coordinates.items()}

    def _get_dataset_tiles(self, coordinates):
        dataset_tile_size = self.dataset.tile_size
        col_min = int(coordinates["x_min"] / dataset_tile_size)
        row_min = int(coordinates["y_min"] / dataset_tile_size)
        col_max = ceil(coordinates["x_max"] / dataset_tile_size)
        row_max = ceil(coordinates["y_max"] / dataset_tile_size)
        return {
            "col_min": col_min,
            "col_max": col_max,
            "row_min": row_min,
            "row_max": row_max,
        }

    def _slice_by_attribute(self, level, column, row, dzi_tile_size):

        dzi_coordinates = self._get_dzi_tile_coordinates(
            row, column, dzi_tile_size, level
        )
        zoom_scale_factor = self._get_zoom_scale_factor(level)
        dataset_tiles = self._get_dataset_tiles(
            self._get_dataset_tile_coordinates(dzi_coordinates, zoom_scale_factor)
        )
        array = self.dataset.array
        try:
            data = (
                array[
                    dataset_tiles["row_min"] : dataset_tiles["row_max"],
                    dataset_tiles["col_min"] : dataset_tiles["col_max"],
                ]
                / 100.0
            )
            if data.shape < (
                dataset_tiles["row_max"] - dataset_tiles["row_min"],
                dataset_tiles["col_max"] - dataset_tiles["col_min"],
            ):
                self.logger.debug(f"### DATA SHAPE IS {data.shape}")
                width = dataset_tiles["col_max"] - dataset_tiles["col_min"]
                height = dataset_tiles["row_max"] - dataset_tiles["row_min"]
                data = np.pad(
                    data,
                    [(0, height - data.shape[0]), (0, width - data.shape[1])],
                    "constant",
                    constant_values=[0],
                )
        except Exception as ex:
            self.logger.error(ex)
            empty_tile = np.zeros(
                (
                    dataset_tiles["col_max"] - dataset_tiles["col_min"],
                    dataset_tiles["row_max"] - dataset_tiles["row_min"],
                )
            )
            return empty_tile, zoom_scale_factor
        return data, zoom_scale_factor

    def _apply_palette(self, tile):
        colored_tile = self.palette(tile)
        return colored_tile

    def _tile_to_img(self, tile, mode="RGBA"):
        img = Image.fromarray(np.uint8(tile), mode)
        return img

    def _get_expected_tile_size(
        self, dzi_tile_size, zoom_scale_factor, dataset_tile_size
    ):
        return max(int((dzi_tile_size * zoom_scale_factor) / dataset_tile_size), 1)

    def _apply_threshold(self, slice, threshold):
        slice[slice < threshold] = np.nan
        return slice

    def _slice_to_tile(
        self, slice, tile_size, zoom_scale_factor, dataset_tile_size, threshold
    ):
        expected_tile_size = self._get_expected_tile_size(
            tile_size, zoom_scale_factor, dataset_tile_size
        )
        if threshold:
            slice = self._apply_threshold(slice, float(threshold))
        tile = self._apply_palette(slice)
        tile = self._tile_to_img(tile)
        # self.logger.debug(f'Tile width: {tile.width} --- Tile Height: {tile.height}')
        # self.logger.debug(f'Expected tile size {expected_tile_size}')
        return tile.resize(
            (
                int(tile_size * (tile.width / expected_tile_size)),
                int(tile_size * (tile.height / expected_tile_size)),
            ),
            Image.BOX,
        )

    def get_dzi_description(self, tile_size=None, array_label=None):
        dset_dims = self._get_dataset_dzi_dimensions()
        tile_size = tile_size or self.conf.DEEPZOOM_TILE_SIZE
        dzi_root = etree.Element(
            "Image",
            attrib={
                "Format": "png",
                "Overlap": "0",  # no overlap when rendering array datasets
                "TileSize": str(tile_size),
            },
            nsmap={None: "http://schemas.microsoft.com/deepzoom/2008"},
        )
        etree.SubElement(
            dzi_root,
            "Size",
            attrib={
                "Height": str(dset_dims["height"]),
                "Width": str(dset_dims["width"]),
            },
        )
        return etree.tostring(dzi_root).decode("utf-8")

    def get_tile(
        self,
        level,
        row,
        column,
        threshold=None,
        tile_size=None,
    ):
        self.logger.debug("Loading tile")
        tile_size = tile_size or self.conf.DEEPZOOM_TILE_SIZE
        self.logger.debug("Setting tile size to %dpx", tile_size)
        slice, zoom_scale_factor = self._slice_by_attribute(
            int(level), int(row), int(column), tile_size
        )

        return self._slice_to_tile(
            slice,
            tile_size,
            zoom_scale_factor,
            self.dataset.tile_size,
            threshold,
        )


class DZIAdapterFactory:
    def __init__(
        self, array_dataset_type, palette: "Palette" = None, conf: Configuration = None
    ):
        self.array_dataset_type = array_dataset_type
        self.conf = conf
        self.palette = palette or Palettable()

    def get_adapter(self, fname) -> DZIAdapter:
        logger.info("Loading TileDB adapter")
        return HeatmapDZIAdapter(DatasetFactory().get(fname), self.palette, self.conf)

        logger.warning("There is no adapter for array type %s", self.array_dataset_type)
        raise UnknownDZIAdaperType(
            "%s is not a valid array dataset type" % self.array_dataset_type
        )


class Palette(abc.ABC):
    @abc.abstractmethod
    def __call__(self, tile: np.ndarray) -> np.ndarray:
        ...


class Palettable(Palette):
    def __init__(self, name: str = "Blues_3"):
        try:
            self._palette = getattr(palettes, name)
        except AttributeError:
            raise InvalidColorPalette("%s is not a valid color palette" % name)

    def __call__(self, tile: np.ndarray) -> np.ndarray:
        p_colors = copy(self._palette.colors)
        p_colors.insert(0, [255, 255, 255])  # TODO: check if actually necessary
        colored_slice = np.full((*tile.shape, 4), [0, 0, 0, 0]).reshape(-1, 4)
        norm_slice = np.asarray(np.float16(tile * len(p_colors))).reshape(-1)
        # extend the p_colors array to avoid an issue related to probabilities with a value of 1.0
        p_colors.append(p_colors[-1])
        for i, prob in enumerate(norm_slice):
            try:
                colored_slice[i] = [*p_colors[int(prob)], 255]
            except ValueError:
                pass
        colored_tile = colored_slice.reshape(*tile.shape, 4)
        return colored_tile
