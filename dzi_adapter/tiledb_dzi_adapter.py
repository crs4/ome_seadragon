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
import tiledb
from lxml import etree

from .dzi_adapter_interface import DZIAdapterInterface
from .. import settings


class TileDBDZIAdapter(DZIAdapterInterface):

    def __init__(self, tiledb_file, tiledb_repo):
        super(DZIAdapterInterface, self).__init__()
        self.tiledb_resource = os.path.join(tiledb_repo, tiledb_file)

    def _get_attributes(self, keys):
        with tiledb.open(self.tiledb_resource) as A:
            attributes = dict()
            for k in keys:
                try:
                    attributes[k] = A.meta[k]
                except:
                    self.logger('Error when loading attribute %s' % k)
        return attributes

    def get_dzi_description(self, tile_size=None):
        """
        with tiledb.open(os.path.join(TILEDB_REPO, 'prostata_1.ndpi.tissue'), 'w') as A:
        A.meta['tile_size'] = 256
        A.meta['original_width'] = tissue_data.shape[0]
        A.meta['original_height'] = tissue_data.shape[1]
        A.meta['dzi_sampling_level'] = 19
        A.meta['rows'] = tissue_probs.shape[0]
        A.meta['columns'] = tissue_probs.shape[1]
        """
        attrs = self._get_attributes(['original_width', 'original_height'])
        tile_size = tile_size if tile_size is not None else settings.DEEPZOOM_TILE_SIZE
        dzi_root = etree.Element(
            'Image',
            attrib={
                'Format': str(settings.DEEPZOOM_FORMAT),
                'Overlap': str(settings.DEEPZOOM_OVERLAP),
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


    def get_tile(self, level, column, row, attribute=None, tile_size=None):
        pass
