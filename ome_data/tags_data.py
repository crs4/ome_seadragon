import omero
from omero.gateway import TagAnnotationWrapper

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


def _image_to_json(image_object):
    return {
        'id': image_object.getId(),
        'type': 'image',
        'fileset_id': image_object.getFileset().getId(),
        'name': image_object.getName()
    }


def _get_images_by_tag(tag_id, connection):
    switch_to_default_search_group(connection)
    imgs_generator = connection.getObjectsByAnnotations('Image', [tag_id])
    images = list()
    for img in imgs_generator:
        images.append(_image_to_json(img))
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
        tags_map = get_tags_list(ts.getId(), connection, fetch_images, append_raw_object=True)
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


def get_tags_list(tagset_id, connection, fetch_images=False, append_raw_object=False):
    switch_to_default_search_group(connection)
    tags = list()
    tagset = connection.getObject('TagAnnotation', tagset_id)
    if tagset is None:
        return None
    for t in tagset.listTagsInTagset():
        imgs_list = list()
        if fetch_images:
            imgs_list = _get_images_by_tag(t.getId(), connection)
        tag_json = _tag_to_json(t, imgs_list)
        if append_raw_object:
            tag_json['obj'] = t
        tags.append(tag_json)
    return tags


def get_images(tag_id, connection):
    return _get_images_by_tag(tag_id, connection)


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
