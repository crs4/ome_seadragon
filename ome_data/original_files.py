#  Copyright (c) 2019, CRS4
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

import omero.model as om
import omero.rtypes as ot
from omero.model.enums import ChecksumAlgorithmSHA1160

from utils import switch_to_default_search_group

import logging


logger = logging.getLogger(__name__)


class DuplicatedEntryError(Exception):
    pass


def save_original_file(connection, name, path, mimetype, size, sha1):
    of = get_original_file(connection, name, mimetype)
    if of is None:
        of = om.OriginalFileI()
        of.setName(ot.wrap(name))
        of.setPath(ot.wrap(path))
        of.setMimetype(ot.wrap(mimetype))
        of.setSize(ot.rlong(size))
        of.setHash(ot.wrap(sha1))
        hasher = om.ChecksumAlgorithmI()
        hasher.setValue(ot.wrap(ChecksumAlgorithmSHA1160))
        of.setHasher(hasher)
        of = connection.getUpdateService().saveAndReturnObject(of)
        return of.getId().getValue()
    else:
        raise DuplicatedEntryError(
            'OriginalFile with name %s and mimetype %s already exists' % (name, mimetype)
        )


def get_original_files(connection, name, mimetype=None):
    switch_to_default_search_group(connection)
    query_filter = {'name': name}
    if mimetype:
        query_filter['mimetype'] = mimetype
    return list(connection.getObjects('OriginalFile', attributes=query_filter))


def get_original_file(connection, name, mimetype):
    ofiles = get_original_files(connection, name, mimetype)
    if len(ofiles) == 0:
        return None
    elif len(ofiles) == 1:
        return ofiles[0]
    else:
        raise DuplicatedEntryError('File %s with mimetype %s is not unique' %
                                   (name, mimetype))


def delete_original_files(connection, name, mimetype=None):
    ofiles = get_original_files(connection, name, mimetype)
    of_ids = []
    if len(ofiles) > 0:
        of_ids = [of.getId() for of in ofiles]
        try:
            connection.deleteObjects('OriginalFile', of_ids, deleteAnns=False,
                                     deleteChildren=False)
        except:
            return False, 0
    return True, len(of_ids)


def get_original_file_infos(connection, name, mimetype):
    ofile = get_original_file(connection, name, mimetype)
    if ofile:
        return {
            'file_path': ofile.getPath(),
            'file_hash': ofile.getHash()
        }
