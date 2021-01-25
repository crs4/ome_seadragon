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


from .. import settings
from .errors import UnknownDZIAdaperType


class DZIAdapterFactory(object):
    
    def __init__(self, array_dataset_type):
        self.array_dataset_type = array_dataset_type

    def _get_tiledb_adapter(self, fname):
        from .tiledb_dzi_adapter import TileDBDZIAdapter

        print(fname, settings.TILEDB_REPOSITORY)

        return TileDBDZIAdapter(fname, settings.TILEDB_REPOSITORY)

    def get_adapter(self, dataset_label):
        if self.array_dataset_type == 'TILEDB':
            return self._get_tiledb_adapter(dataset_label)
        else:
            raise UnknownDZIAdaperType('%s is not a valid array dataset type' % self.array_dataset_type)
