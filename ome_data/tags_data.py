import omero
from omero.gateway import TagAnnotationWrapper

from projects_datasets import _image_to_json
from utils import switch_to_default_search_group


def _is_tagset(obj):
    try:
        obj.countTagsInTagset()
        return True
    except TypeError:
        return False


def _tag_to_json(tag_object, images_list):
    return {
        'id': tag_object.getId(),
        'type': 'tag',
        'value': tag_object.getValue(),
        'description': tag_object.getDescription(),
        'images': images_list
    }


def _tagset_to_json(tagset_object, tags_map=None):
    if not tags_map:
        tags_map = list()
    return {
        'id': tagset_object.getId(),
        'type': 'tagset',
        'value': tagset_object.getValue(),
        'description': tagset_object.getDescription(),
        'tags': tags_map
    }


def _get_tags_list(connection, tagset_obj, fetch_images=False, append_raw_object=False):
    tags = list()
    for t in tagset_obj.listTagsInTagset():
        images = list()
        if fetch_images:
            images = _get_images_by_tag(t.getId(), connection)
        tag_json = _tag_to_json(t, images)
        if append_raw_object:
            tag_json['obj'] = t
        tags.append(tag_json)
    return tags


def _get_images_by_tag(tag_id, connection):
    switch_to_default_search_group(connection)
    imgs_generator = connection.getObjectsByAnnotations('Image', [tag_id])
    images = list()
    for img in imgs_generator:
        images.append(_image_to_json(img, connection))
    return images


def get_annotations_list(connection, fetch_images=False):
    switch_to_default_search_group(connection)
    tag_sets = list()
    tags = list()
    for t in connection.getObjects("TagAnnotation"):
        if _is_tagset(t):
            tag_sets.append(t)
        else:
            tags.append(t)
    annotations = list()
    for ts in tag_sets:
        tags_map = _get_tags_list(connection, ts, fetch_images, append_raw_object=True)
        for tmi in tags_map:
            tobj = tmi.pop('obj')
            try:
                tags.pop(tags.index(tobj))
            except ValueError:
                pass
        tagset_json = _tagset_to_json(ts, tags_map)
        annotations.append(tagset_json)
    for t in tags:
        imgs_list = list()
        if fetch_images:
            imgs_list = _get_images_by_tag(t.getId(), connection)
        annotations.append(_tag_to_json(t, imgs_list))
    return annotations


def get_tagset(connection, tagset_id, fetch_tags=False, fetch_images=False):
    switch_to_default_search_group(connection)
    tagset = connection.getObject('TagAnnotation', tagset_id)
    if tagset is not None and _is_tagset(tagset):
        tags_map = list()
        if fetch_tags:
            tags_map = _get_tags_list(connection, tagset, fetch_images)
        return _tagset_to_json(tagset, tags_map)
    else:
        return None


def get_tag(connection, tag_id, fetch_images=False):
    switch_to_default_search_group(connection)
    tag = connection.getObject('TagAnnotation', tag_id)
    if tag is not None and not _is_tagset(tag):
        images = list()
        if fetch_images:
            images = _get_images_by_tag(tag_id, connection)
        return _tag_to_json(tag, images)
    else:
        return None


def find_annotations(search_pattern, connection, fetch_images=False):
    switch_to_default_search_group(connection)
    query_service = connection.getQueryService()
    query_params = omero.sys.ParametersI()
    query_params.addString('search_pattern', '%%%s%%' % search_pattern)
    query = '''
    SELECT t FROM TagAnnotation t
    WHERE lower(t.description) LIKE lower(:search_pattern)
    OR lower(t.textValue) LIKE lower(:search_pattern)
    '''
    annotations = list()
    for res in query_service.findAllByQuery(query, query_params):
        res = TagAnnotationWrapper(connection, res)
        if _is_tagset(res):
            annotations.append(_tagset_to_json(res))
        else:
            imgs_list = list()
            if fetch_images:
                imgs_list = _get_images_by_tag(res.getId(), connection)
            annotations.append(_tag_to_json(res, imgs_list))
    return annotations
