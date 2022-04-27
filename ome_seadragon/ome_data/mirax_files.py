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

import os
import logging

logger = logging.getLogger(__name__)


class InvalidMiraxFile(Exception):
    pass


class InvalidMiraxFolder(Exception):
    pass


def get_mirax_files_paths(slide_base_name):
    if settings.MIRAX_FOLDER is not None:
        mirax_files = (
            os.path.join(settings.MIRAX_FOLDER, '{0}.mrxs'.format(slide_base_name)),
            os.path.join(settings.MIRAX_FOLDER, slide_base_name)
        )
        if os.path.isfile(mirax_files[0]):
            if os.path.isdir(mirax_files[1]):
                return mirax_files
            else:
                raise InvalidMiraxFolder('Path {0} not found'.format(mirax_files[1]))
        else:
            raise InvalidMiraxFile('File {0} not found'.format(mirax_files[0]))
    else:
        raise settings.ServerConfigError('MIRAX default folder was not configured properly')
