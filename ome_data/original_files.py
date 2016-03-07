# import omero
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
