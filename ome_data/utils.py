from ome_seadragon import settings


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
