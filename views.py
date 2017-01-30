from ome_seadragon.ome_data import tags_data, projects_datasets, original_files
from ome_seadragon.ome_data.original_files import DuplicatedEntryError
from ome_seadragon import settings
from ome_seadragon.slides_manager import RenderingEngineFactory

import logging
import re
from distutils.util import strtobool
try:
    import simplejson as json
except ImportError:
    import json

from omeroweb.webclient.decorators import login_required

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render

logger = logging.getLogger(__name__)


def check_app(request):
    return HttpResponse("ome_seadragon working!")


def check_repository(request):
    if settings.IMGS_REPOSITORY:
        return HttpResponse(settings.IMGS_REPOSITORY)
    else:
        return HttpResponse("No repository has been configured")


@login_required()
def start_connection(request, conn=None, **kwargs):
    public_user_allowed = strtobool(request.GET.get('allow_public_user', default='true'))
    if not public_user_allowed:
        if settings.OME_PUBLIC_USER is None:
            return HttpResponseServerError('"omero.web.ome_seadragon.ome_public_user" property was not configured on the server')
        if conn.getUser().getName() == settings.OME_PUBLIC_USER:
            return HttpResponse('Unauthorized', status=401)
    return HttpResponse(status=204)


@login_required()
def check_image_path(request, image_id, conn=None, **kwargs):
    rendering_engine = RenderingEngineFactory().get_tiles_rendering_engine(image_id, conn)
    return HttpResponse(rendering_engine._get_image_path())


def get_example_viewer(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    mirax = strtobool(request.GET.get('mirax_image', default='false'))
    return render(request, 'ome_seadragon/test/test_viewer.html',
                  {'image_id': image_id, 'host_name': base_url, 'mirax': mirax})


def get_example_viewer_json(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    mirax = strtobool(request.GET.get('mirax_image', default='false'))
    return render(request, 'ome_seadragon/test/test_viewer_json.html',
                  {'image_id': image_id, 'host_name': base_url, 'mirax': mirax})


def get_example_annotations(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    mirax = strtobool(request.GET.get('mirax_image', default='false'))
    return render(request, 'ome_seadragon/test/test_annotations.html',
                  {'image_id': image_id, 'host_name': base_url, 'mirax': mirax})


def get_example_ome_rois(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    return render(request, 'ome_seadragon/test/test_ome_roi.html',
                  {'image_id': image_id, 'host_name': base_url})


def get_example_interactive_markers(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    mirax = strtobool(request.GET.get('mirax_image', default='false'))
    return render(request, 'ome_seadragon/test/test_markers.html',
                  {'image_id': image_id, 'host_name': base_url, 'mirax': mirax})


def get_example_interactive_polygons(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    mirax = strtobool(request.GET.get('mirax_image', default='false'))
    return render(request, 'ome_seadragon/test/test_polygons.html',
                  {'image_id': image_id, 'host_name': base_url, 'mirax': mirax})


def get_example_interactive_rulers(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    mirax = strtobool(request.GET.get('mirax_image', default='false'))
    return render(request, 'ome_seadragon/test/test_rulers.html',
                  {'image_id': image_id, 'host_name': base_url, 'mirax': mirax})


def get_example_interactive_freehand(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    mirax = strtobool(request.GET.get('mirax_image', default='false'))
    return render(request, 'ome_seadragon/test/test_freehand_drawing.html',
                  {'image_id': image_id, 'host_name': base_url, 'mirax': mirax})


@login_required()
def get_projects(request, conn=None, **kwargs):
    try:
        fetch_datasets = strtobool(request.GET.get('datasets'))
    except (ValueError, AttributeError):
        fetch_datasets = False
    projects = projects_datasets.get_projects(conn, fetch_datasets)
    return HttpResponse(json.dumps(projects), content_type='application/json')


@login_required()
def get_project(request, project_id, conn=None, **kwargs):
    try:
        fetch_datasets = strtobool(request.GET.get('datasets'))
    except (ValueError, AttributeError):
        fetch_datasets = False
    try:
        fetch_images = strtobool(request.GET.get('images'))
    except (ValueError, AttributeError):
        fetch_images = False
    try:
        expand_series = strtobool(request.GET.get('full_series'))
    except (ValueError, AttributeError):
        expand_series = False
    project = projects_datasets.get_project(conn, project_id, fetch_datasets, fetch_images,
                                            expand_series)
    return HttpResponse(json.dumps(project), content_type='application/json')


@login_required()
def get_dataset(request, dataset_id, conn=None, **kwargs):
    try:
        fetch_images = strtobool(request.GET.get('images'))
    except (ValueError, AttributeError):
        fetch_images = False
    try:
        expand_series = strtobool(request.GET.get('full_series'))
    except (ValueError, AttributeError):
        expand_series = False
    dataset = projects_datasets.get_dataset(conn, dataset_id, fetch_images,
                                            expand_series)
    return HttpResponse(json.dumps(dataset), content_type='application/json')


@login_required()
def get_image(request, image_id, conn=None, **kwargs):
    try:
        fetch_rois = strtobool(request.GET.get('rois'))
    except (ValueError, AttributeError):
        fetch_rois = False
    image = projects_datasets.get_image(conn, image_id, fetch_rois)
    return HttpResponse(json.dumps(image), content_type='application/json')


@login_required()
def get_images_quick_list(request, conn=None, **kwargs):
    try:
        expand_series = strtobool(request.GET.get('full_series'))
    except (ValueError, AttributeError):
        expand_series = False
    images_list = projects_datasets.get_images_quick_list(conn, expand_series)
    return HttpResponse(json.dumps(images_list), content_type='application/json')


@login_required()
def get_annotations(request, conn=None, **kwargs):
    try:
        fetch_images = strtobool(request.GET.get('fetch_imgs'))
    except (ValueError, AttributeError):
        fetch_images = False
    annotations = tags_data.get_annotations_list(conn, fetch_images)
    return HttpResponse(json.dumps(annotations), content_type='application/json')


@login_required()
def get_tagset(request, tagset_id, conn=None, **kwargs):
    try:
        fetch_tags = strtobool(request.GET.get('tags'))
    except (ValueError, AttributeError):
        fetch_tags = False
    try:
        fetch_images = strtobool(request.GET.get('images'))
    except (ValueError, AttributeError):
        fetch_images = False
    tagset = tags_data.get_tagset(conn, tagset_id, fetch_tags, fetch_images)
    return HttpResponse(json.dumps(tagset), content_type='application/json')


@login_required()
def get_tag(request, tag_id, conn=None, **kwargs):
    try:
        fetch_images = strtobool(request.GET.get('images'))
    except (ValueError, AttributeError):
        fetch_images = False
    tag = tags_data.get_tag(conn, tag_id, fetch_images)
    return HttpResponse(json.dumps(tag), content_type='application/json')


@login_required()
def find_annotations(request, conn=None, **kwargs):
    search_pattern = request.GET.get('query')
    try:
        fetch_images = strtobool(request.GET.get('fetch_imgs'))
    except (ValueError, AttributeError):
        fetch_images = False
    logger.debug('"fetch_imgs" value %r', fetch_images)
    annotations = tags_data.find_annotations(search_pattern, conn, fetch_images)
    return HttpResponse(json.dumps(annotations), content_type='application/json')


@login_required()
def get_image_dzi(request, image_id, fetch_original_file=False,
                  file_mimetype=None, conn=None, **kwargs):
    rf = RenderingEngineFactory()
    rendering_engine = rf.get_primary_tiles_rendering_engine(image_id, conn)
    try:
        dzi_metadata = rendering_engine.get_dzi_description(fetch_original_file, file_mimetype)
    except Exception, e:
        rendering_engine = rf.get_secondary_tiles_rendering_engine(image_id, conn)
        if rendering_engine:
            dzi_metadata = rendering_engine.get_dzi_description(fetch_original_file, file_mimetype)
        else:
            raise e
    if dzi_metadata:
        return HttpResponse(dzi_metadata, content_type='application/xml')
    else:
        return HttpResponseNotFound('No image with ID %s' % image_id)


@login_required()
def get_image_json(request, image_id, fetch_original_file=False,
                   file_mimetype=None, conn=None, **kwargs):
    rf = RenderingEngineFactory()
    rendering_engine = rf.get_primary_tiles_rendering_engine(image_id, conn)
    resource_path = request.build_absolute_uri('%s_files/' % image_id)
    try:
        json_metadata = rendering_engine.get_json_description(resource_path, fetch_original_file,
                                                              file_mimetype)
    except Exception, e:
        rendering_engine = rf.get_secondary_tiles_rendering_engine(image_id, conn)
        if rendering_engine:
            json_metadata = rendering_engine.get_json_description(resource_path, fetch_original_file,
                                                                  file_mimetype)
        else:
            raise e
    if json_metadata:
        return HttpResponse(json.dumps(json_metadata), content_type='application/json')
    else:
        return HttpResponseNotFound('No image with ID %s' % image_id)


@login_required()
def get_image_metadata(request, image_id, fetch_original_file=False, file_mimetype=None, conn=None, **kwargs):
    rf = RenderingEngineFactory()
    rendering_engine = rf.get_primary_tiles_rendering_engine(image_id, conn)
    resource_path = request.build_absolute_uri('%s_files/' % image_id)
    try:
        img_metadata = rendering_engine.get_image_description(resource_path, fetch_original_file, file_mimetype)
    except Exception, e:
        rendering_engine = rf.get_secondary_tiles_rendering_engine(image_id, conn)
        if rendering_engine:
            img_metadata = rendering_engine.get_image_description(resource_path, fetch_original_file, file_mimetype)
        else:
            raise e
    if img_metadata:
        return HttpResponse(json.dumps(img_metadata), content_type='application/json')
    else:
        return HttpResponseNotFound('No image with ID %s' % image_id)


@login_required()
def get_image_thumbnail(request, image_id, fetch_original_file=False,
                        file_mimetype=None, conn=None, **kwargs):
    rf = RenderingEngineFactory()
    rendering_engine = rf.get_primary_thumbnails_rendering_engine(image_id, conn)
    try:
        thumbnail, image_format = rendering_engine.get_thumbnail(int(request.GET.get('size')),
                                                                 fetch_original_file, file_mimetype)
    except Exception, e:
        rendering_engine = rf.get_secondary_thumbnails_rendering_engine(image_id, conn)
        if rendering_engine:
            thumbnail, image_format = rendering_engine.get_thumbnail(int(request.GET.get('size')),
                                                                     fetch_original_file, file_mimetype)
        else:
            raise e
    if thumbnail:
        response = HttpResponse(content_type="image/%s" % image_format)
        thumbnail.save(response, image_format)
        return response
    else:
        return HttpResponseServerError('Unable to load thumbnail')


@login_required()
def get_tile(request, image_id, level, column, row, tile_format,
             fetch_original_file=False, file_mimetype=None, conn=None, **kwargs):
    if tile_format != settings.DEEPZOOM_FORMAT:
        return HttpResponseServerError("Format %s not supported by the server" % tile_format)
    rf = RenderingEngineFactory()
    rendering_engine = rf.get_primary_tiles_rendering_engine(image_id, conn)
    try:
        tile, image_format = rendering_engine.get_tile(int(level), int(column), int(row),
                                                       fetch_original_file, file_mimetype)
    except Exception, e:
        rendering_engine = rf.get_secondary_tiles_rendering_engine(image_id, conn)
        if rendering_engine:
            tile, image_format = rendering_engine.get_tile(int(level), int(column), int(row),
                                                           fetch_original_file, file_mimetype)
        else:
            raise e
    if tile:
        response = HttpResponse(content_type='image/%s' % image_format)
        tile.save(response, image_format)
        return response
    else:
        return HttpResponseNotFound('No tile can be found')


@login_required()
def get_image_mpp(request, image_id, fetch_original_file=False,
                  file_mimetype=None, conn=None, **kwargs):
    rf = RenderingEngineFactory()
    rendering_engine = rf.get_primary_tiles_rendering_engine(image_id, conn)
    try:
        image_mpp = rendering_engine.get_openseadragon_config(fetch_original_file, file_mimetype)['mpp']
    except Exception, e:
        rendering_engine = rf.get_secondary_tiles_rendering_engine(image_id, conn)
        if rendering_engine:
            image_mpp = rendering_engine.get_openseadragon_config(fetch_original_file, file_mimetype)['mpp']
        else:
            raise e
    return HttpResponse(json.dumps({'image_mpp': image_mpp}), content_type='application/json')


@login_required()
def register_original_file(request, conn=None, **kwargs):
    try:
        fname = request.GET.get('name')
        if not re.match(r'^[\w\-.]+$', fname):
            return HttpResponseServerError('Invalid file name received: %s' % fname)
        fpath = request.GET.get('path')
        fmtype = request.GET.get('mimetype')
        if not all([fname, fpath, fmtype]):
            return HttpResponseServerError('Mandatory field missing')
        file_id = original_files.save_original_file(conn, fname, fpath, fmtype,
                                                    int(request.GET.get('size', default=-1)),
                                                    request.GET.get('sha1', default='UNKNOWN'))
        return HttpResponse(json.dumps({'omero_id': file_id}), content_type='application/json')
    except DuplicatedEntryError, dee:
        return HttpResponseServerError(dee.message)


@login_required()
def delete_original_file(request, file_name, conn=None, **kwargs):
    fmtype = request.GET.get('mimetype')
    if fmtype is None:
        return HttpResponseServerError('Missing mandatory mimetype value to complete the request')
    status, count = original_files.delete_original_files(conn, file_name, fmtype)
    return HttpResponse(json.dumps({'success': status, 'deleted_count': count}),
                        content_type='application/json')


@login_required()
def delete_original_files(request, file_name, conn=None, **kwargs):
    status, count = original_files.delete_original_files(conn, file_name)
    return HttpResponse(json.dumps({'success': status, 'deleted_count': count}),
                        content_type='application/json')
