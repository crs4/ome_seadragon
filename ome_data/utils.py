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

from ome_seadragon import settings
from copy import copy


def _get_group_id_by_name(group_name, connection):
    group = connection.getObject('ExperimenterGroup', attributes={'name': group_name})
    if group:
        return group.id
    else:
        return None


def _get_current_group_id(connection):
    return connection.getGroupFromContext().id


def switch_to_default_search_group(connection):
    if settings.DEFAULT_SEARCH_GROUP:
        group_id = _get_group_id_by_name(settings.DEFAULT_SEARCH_GROUP, connection)
        if group_id and (group_id != _get_current_group_id(connection)):
            connection.setGroupForSession(group_id)


def _adapt_ellipse_roi(roi_json):
    new_json = copy(roi_json)
    try:
        new_json['cx'] = new_json.pop('x')
        new_json['cy'] = new_json.pop('y')
        new_json['rx'] = new_json.pop('radiusX')
        new_json['ry'] = new_json.pop('radiusY')
    except KeyError:
        pass
    return new_json


def adapt_rois_json(rois):
    adapted_rois = list()
    for r in rois:
        if r['type'] == 'Ellipse':
            adapted_rois.append(_adapt_ellipse_roi(r))
        else:
            adapted_rois.append(r)
    return adapted_rois
