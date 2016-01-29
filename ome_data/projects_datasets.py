from time import mktime

import omero
import omero.model
from omeroweb.webgateway.marshal import rgb_int2css

from utils import switch_to_default_search_group


def _date_to_timestamp(date):
    return mktime(date.timetuple())


def _get_image_resolution(image_object):
    return image_object.getSizeX() * image_object.getSizeY()


def _project_to_json(project_object, datasets_map=None):
    prj_json = {
        'id': project_object.getId(),
        'name': project_object.getName(),
        'description': project_object.getDescription(),
        'datasets': []
    }
    if datasets_map is not None:
        for dset, imgs in datasets_map:
            prj_json['datasets'].append(_dataset_to_json(dset, imgs))
    return prj_json


def _dataset_to_json(dataset_object, image_objects=None):
    dset_obj = {
        'id': dataset_object.getId(),
        'type': dataset_object.OMERO_CLASS,
        'name': dataset_object.getName(),
        'description': dataset_object.getDescription(),
        'child_count': dataset_object.countChildren(),
        'images': []
    }
    if image_objects is not None:
        for img_obj in image_objects:
            dset_obj['images'].append(_image_to_json(img_obj))
    return dset_obj


def _image_to_json(image_object, full_info=False, roi_objects=None):
    img_obj = {
        'id': image_object.getId(),
        'type': 'image',
        'description': image_object.getDescription(),
        'name': image_object.getName(),
        'author': image_object.getAuthor(),
        'creation_time': _date_to_timestamp(image_object.getDate()),
        'import_time': _date_to_timestamp(image_object.creationEventDate()),
        'last_update': _date_to_timestamp(image_object.updateEventDate()),
        'rois': []
    }
    if full_info:
        img_obj.update({
            'fileset_id': image_object.getFileset().getId(),
            'project_id': image_object.getProject().getId(),
            'project_name': image_object.getProject().getName(),
            'project_description': image_object.getProject().getDescription(),
            'dataset_id': image_object.getParent().getId(),
            'dataset_name': image_object.getParent().getName(),
            'dataset_description': image_object.getParent().getDescription()
        })
    if roi_objects is not None:
        for roi in roi_objects:
            img_obj['rois'].append(_roi_to_json(roi))
    return img_obj


def _roi_to_json(roi_object):
    return {
        'id': roi_object.getId().getValue(),
        'shapes': [_shape_to_json(s) for s in roi_object.copyShapes()]
    }


def _shape_to_json(shape_object):
    sh_obj = {
        'id': shape_object.getId().getValue(),
        'the_t': shape_object.getTheT().getValue(),
        'the_z': shape_object.getTheZ().getValue(),
        'stroke_width': int(shape_object.getStrokeWidth().getValue()),
        'stroke_color': rgb_int2css(shape_object.getStrokeColor().getValue())[0],
        'stroke_alpha': rgb_int2css(shape_object.getStrokeColor().getValue())[1],
        'fill_color': rgb_int2css(shape_object.getFillColor().getValue())[0],
        'fill_alpha': rgb_int2css(shape_object.getFillColor().getValue())[1],
        'transform': shape_object.getTransform().getValue()
    }
    if shape_object.getTextValue():
        sh_obj['text_value'] = shape_object.getTextValue().getValue()
    if type(shape_object) == omero.model.RectangleI:
        sh_obj['type'] = 'Rectangle'
        sh_obj['x'] = shape_object.getX().getValue()
        sh_obj['y'] = shape_object.getY().getValue()
        sh_obj['width'] = shape_object.getWidth().getValue()
        sh_obj['height'] = shape_object.getHeight().getValue()
    elif type(shape_object) == omero.model.EllipseI:
        sh_obj['type'] = 'Ellipse'
        sh_obj['cx'] = shape_object.getCx().getValue()
        sh_obj['cy'] = shape_object.getCy().getValue()
        sh_obj['rx'] = shape_object.getRx().getValue()
        sh_obj['ry'] = shape_object.getRy().getValue()
    elif type(shape_object) == omero.model.PointI:
        sh_obj['type'] = 'Point'
        sh_obj['cx'] = shape_object.getCx().getValue()
        sh_obj['cy'] = shape_object.getCy().getValue()
    elif type(shape_object) == omero.model.LineI:
        sh_obj['type'] = 'Line'
        sh_obj['x1'] = shape_object.getX1().getValue()
        sh_obj['y1'] = shape_object.getY1().getValue()
        sh_obj['x2'] = shape_object.getX2().getValue()
        sh_obj['y2'] = shape_object.getY2().getValue()
    else:
        sh_obj['type'] = 'UNKNOWN'
    return sh_obj


def _get_images_for_dataset(dataset_object, reduce_series=True):
    imgs = list(dataset_object.listChildren())
    if reduce_series:
        imgs_map = {}
        for img in imgs:
            imgs_map.setdefault(img.getFileset().getId(), {})[_get_image_resolution(img)] = img
        filtered_images = []
        for files in imgs_map.itervalues():
            filtered_images.append(files[max(files.keys())])
        return filtered_images
    else:
        return imgs


def get_projects(connection, fetch_datasets=False):
    switch_to_default_search_group(connection)
    projects = list(connection.listProjects())
    projects_json = []
    for proj in projects:
        if fetch_datasets:
            datasets = list(proj.listChildren())
        else:
            datasets = []
        projects_json.append(_project_to_json(proj, ((d, []) for d in datasets)))
    return projects_json


def get_project(connection, project_id, fetch_datasets=False, fetch_images=False):
    switch_to_default_search_group(connection)
    project = connection.getObject('Project', project_id)
    if project is not None:
        datasets_map = []
        if fetch_datasets:
            datasets = list(project.listChildren())
            for ds in datasets:
                if fetch_images:
                    images = _get_images_for_dataset(ds)
                else:
                    images = []
                datasets_map.append((ds, images))
        return _project_to_json(project, datasets_map)
    return None


def get_dataset(connection, dataset_id, fetch_images=False):
    switch_to_default_search_group(connection)
    dataset = connection.getObject('Dataset', dataset_id)
    if dataset is not None:
        if fetch_images:
            images = _get_images_for_dataset(dataset)
        else:
            images = []
        return _dataset_to_json(dataset, images)
    return None


def get_image(connection, image_id, fetch_rois=False):
    switch_to_default_search_group(connection)
    img = connection.getObject('Image', image_id)
    if img is not None:
        if fetch_rois:
            roi_service = connection.getRoiService()
            results = roi_service.findByImage(int(image_id), None)
            rois = list(results.rois)
        else:
            rois = []
        return _image_to_json(img, True, rois)
    return None
