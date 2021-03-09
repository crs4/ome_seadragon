#  Copyright (c) 2021, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import numpy as np
import tiledb
from lxml import etree
from PIL import Image
from copy import copy
import palettable.colorbrewer.sequential as palettes

from .dzi_adapter_interface import DZIAdapterInterface
from .errors import InvalidAttribute, InvalidColorPalette
from .. import settings


class TileDBDZIAdapter(DZIAdapterInterface):

    def __init__(self, tiledb_file, tiledb_repo):
        super(TileDBDZIAdapter, self).__init__()
        self.tiledb_resource = os.path.join(tiledb_repo, tiledb_file)
        self.logger.info('TileDB adapter initialized')

    def _get_meta_attributes(self, keys):
        with tiledb.open(self.tiledb_resource) as A:
            attributes = dict()
            for k in keys:
                try:
                    attributes[k] = A.meta[k]
                except:
                    self.logger('Error when loading attribute %s' % k)
        return attributes

    def _get_schema(self):
        return tiledb.ArraySchema.load(self.tiledb_resource)

    def _check_attribute(self, attribute):
        schema = self._get_schema()
        return schema.has_attr(attribute)

    def _get_attribute_by_index(self, attribute_index):
        schema = self._get_schema()
        if attribute_index >= 0 and attribute_index < schema.nattr:
            return schema.attr(attribute_index).name
        else:
            raise IndexError('Schema has no attribute for index %d' % attribute_index)

    def _slice_by_attribute(self, attribute, level, row, column):
        attrs = self._get_meta_attributes(['dzi_sampling_level', 'tile_size'])
        with tiledb.open(self.tiledb_resource) as A:
            q = A.query(attrs=(attribute,))
            zsf = pow(2, int(attrs['dzi_sampling_level']) - int(level))
            self.logger.info('Required level %d - scale factor %d', level, zsf)
            slice = q[
                int(row)*zsf : (int(row)*zsf)+int(zsf),
                int(column)*zsf : (int(column)*zsf)+int(zsf)
            ][attribute]
        return slice

    def _apply_palette(self, slice, palette):
        try:
            p_obj = getattr(palettes, palette)
        except AttributeError:
            raise InvalidColorPalette('%s is not a valid color palette' % palette)
        p_colors = copy(p_obj.colors)
        p_colors.insert(0, [255, 255, 255]) # TODO: check if actually necessary
        norm_slice = np.asarray(np.uint8(slice*len(p_colors))).reshape(-1)
        colored_slice = [p_colors[int(y)] for y in norm_slice]
        return np.array(colored_slice).reshape(*slice.shape, 3)

    def _tile_to_img(self, tile, mode='RGB'):
        img = Image.fromarray(np.uint8(tile), mode)
        self.logger.info(img)
        return img

    def _upscale_tile(self, tile, tile_size):
        tile = tile.repeat(tile_size/tile.shape[0], axis=0).repeat(tile_size/tile.shape[1], axis=1)
        return self._tile_to_img(tile)

    def _downscale_tile(self, tile, tile_size):
        tile_img = self._tile_to_img(tile)
        return tile_img.resize((tile_size, tile_size), Image.ANTIALIAS)

    def _slice_to_tile(self, slice, tile_size, palette):
        tile = self._apply_palette(slice, palette)
        tile_dim = tile.shape[0]
        if tile_dim == tile_size:
            tile = self._tile_to_img(tile)
        elif tile_dim < tile_size:
            tile = self._upscale_tile(tile, tile_size)
        else:
            tile = self._downscale_tile(tile, tile_size)
        return tile

    def get_dzi_description(self, tile_size=None):
        attrs = self._get_meta_attributes(['original_width', 'original_height'])
        tile_size = tile_size if tile_size is not None else settings.DEEPZOOM_TILE_SIZE
        dzi_root = etree.Element(
            'Image',
            attrib={
                'Format': 'png',
                'Overlap': '0', # no overlap when rendering array datasets
                'TileSize': str(tile_size)
            },
            nsmap={None: 'http://schemas.microsoft.com/deepzoom/2008'}
        )
        etree.SubElement(dzi_root, 'Size',
                         attrib={
                             'Height': str(attrs['original_height']),
                             'Width': str(attrs['original_width'])
                         })
        return etree.tostring(dzi_root)


    def get_tile(self, level, row, column, palette, attribute_label=None, tile_size=None):
        self.logger.info('Loading tile')
        tile_size = tile_size if tile_size is not None else settings.DEEPZOOM_TILE_SIZE
        self.logger.info('Setting tile size to %dpx', tile_size)
        if attribute_label is None:
            attribute = self._get_attribute_by_index(0)
        else:
            if self._check_attribute(attribute_label):
                attribute = attribute_label
            else:
                raise InvalidAttribute('Dataset has no attribute %s' % attribute_label)
        self.logger.info('Slicing by attribute %s', attribute)
        slice = self._slice_by_attribute(attribute, level, row, column)
        return self._slice_to_tile(slice, tile_size, palette)
