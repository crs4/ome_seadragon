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

from time import mktime

from omeroweb.webgateway.marshal import shapeMarshal

from utils import switch_to_default_search_group


def _date_to_timestamp(date):
    return mktime(date.timetuple())


def _get_image_resolution(image_object):
    return image_object.getSizeX() * image_object.getSizeY()


def get_fileset_highest_resolution(image_object, connection):
    fs = connection.getObject('Fileset', image_object.getFileset().getId())
    big_image = None
    for tmp_img in fs.copyImages():
        if big_image is None:
            big_image = tmp_img
        else:
            if (tmp_img.getSizeX() * tmp_img.getSizeY()) > (big_image.getSizeX() * big_image.getSizeY()):
                big_image = tmp_img
    return big_image


def _project_to_json(project_object, connection, datasets_map=None):
    prj_json = {
        'id': project_object.getId(),
        'name': project_object.getName(),
        'description': project_object.getDescription(),
        'datasets': []
    }
    if datasets_map is not None:
        for dset, imgs in datasets_map:
            prj_json['datasets'].append(_dataset_to_json(dset, connection, imgs))
    return prj_json


def _dataset_to_json(dataset_object, connection, image_objects=None):
    dset_obj = {
        'id': dataset_object.getId(),
        'type': dataset_object.OMERO_CLASS,
        'name': dataset_object.getName(),
        'description': dataset_object.getDescription(),
        'childCount': dataset_object.countChildren(),
        'images': []
    }
    if image_objects is not None:
        for img_obj in image_objects:
            dset_obj['images'].append(_image_to_json(img_obj, connection))
    return dset_obj


def _image_to_json(image_object, connection, full_info=False, roi_objects=None):
    img_obj = {
        'id': image_object.getId(),
        'type': 'image',
        'description': image_object.getDescription(),
        'name': image_object.getName(),
        'author': image_object.getAuthor(),
        'width': image_object.getSizeX(),
        'height': image_object.getSizeY(),
        'creationTime': _date_to_timestamp(image_object.getDate()),
        'importTime': _date_to_timestamp(image_object.creationEventDate()),
        'lastUpdate': _date_to_timestamp(image_object.updateEventDate()),
        'rois': [],
        'high_resolution_image': get_fileset_highest_resolution(image_object, connection).getId()
    }
    if full_info:
        img_obj.update({
            'filesetId': image_object.getFileset().getId(),
            'projectId': image_object.getProject().getId(),
            'projectName': image_object.getProject().getName(),
            'projectDescription': image_object.getProject().getDescription(),
            'datasetId': image_object.getParent().getId(),
            'datasetName': image_object.getParent().getName(),
            'datasetDescription': image_object.getParent().getDescription()
        })
    if roi_objects is not None:
        for roi in roi_objects:
            img_obj['rois'].append(_roi_to_json(roi))
    return img_obj


def _roi_to_json(roi_object):
    return {
        'id': roi_object.getId().getValue(),
        'shapes': [shapeMarshal(s) for s in roi_object.copyShapes()]
    }


def _reduce_images_series(images):
    imgs_map = {}
    for img in images:
        imgs_map.setdefault(img.getFileset().getId(), {})[_get_image_resolution(img)] = img
    filtered_images = []
    for files in imgs_map.itervalues():
        filtered_images.append(files[max(files.keys())])
    return filtered_images


def _get_images_for_dataset(dataset_object, reduce_series=True):
    imgs = list(dataset_object.listChildren())
    if reduce_series:
        return _reduce_images_series(imgs)
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
        projects_json.append(_project_to_json(proj, connection=connection,
                                              datasets_map=((d, []) for d in datasets)))
    return projects_json


def get_project(connection, project_id, fetch_datasets=False, fetch_images=False,
                expand_img_series=False):
    switch_to_default_search_group(connection)
    project = connection.getObject('Project', project_id)
    if project is not None:
        datasets_map = []
        if fetch_datasets:
            datasets = list(project.listChildren())
            for ds in datasets:
                if fetch_images:
                    images = _get_images_for_dataset(ds, not expand_img_series)
                else:
                    images = []
                datasets_map.append((ds, images))
        return _project_to_json(project, datasets_map=datasets_map,
                                connection=connection)
    return None


def get_dataset(connection, dataset_id, fetch_images=False, expand_img_series=False):
    switch_to_default_search_group(connection)
    dataset = connection.getObject('Dataset', dataset_id)
    if dataset is not None:
        if fetch_images:
            images = _get_images_for_dataset(dataset, not expand_img_series)
        else:
            images = []
        return _dataset_to_json(dataset, connection=connection, image_objects=images)
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
        return _image_to_json(img, connection, True, rois)
    return None


def get_images_quick_list(connection, expand_imgs_series=False):
    switch_to_default_search_group(connection)
    images_list = []
    # get OMERO images
    imgs = connection.getObjects('Image')
    if not expand_imgs_series:
        imgs = _reduce_images_series(imgs)
    for img in imgs:
        images_list.append(
            {
                'omero_id': img.getId(),
                'name': img.getName(),
                'img_type': 'OMERO_IMG' # right now we only need to separate OMERO imgs from "special" ones like MIRAX
            }
        )
    # get "special" images like MIRAX ones (actually, right now only the MIRAX ones...)
    query_filter = {'mimetype': 'mirax/index'}
    imgs = connection.getObjects('OriginalFile', attributes=query_filter)
    for img in imgs:
        images_list.append(
            {
                'omero_id': img.getId(),
                'name': img.getName(),
                'img_type': 'MIRAX'
            }
        )
    return images_list
