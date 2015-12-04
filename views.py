from ome_seadragon.ome_data import tags_data
from ome_seadragon import settings
from ome_seadragon import slides_manager

import logging
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
def check_image_path(request, image_id, conn=None, **kwargs):
    return HttpResponse(slides_manager._get_image_path(image_id, conn))


def get_example_viewer(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    return render(request, 'ome_seadragon/test/test_viewer.html',
                  {'image_id': image_id, 'host_name': base_url})


def get_example_annotations(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    return render(request, 'ome_seadragon/test/test_annotations.html',
                  {'image_id': image_id, 'host_name': base_url})


def get_example_ome_rois(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    return render(request, 'ome_seadragon/test/test_ome_roi.html',
                  {'image_id': image_id, 'host_name': base_url})


def get_example_custom_handlers(request, image_id):
    base_url = '%s://%s' % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'])
    return render(request, 'ome_seadragon/test/test_events.html',
                  {'image_id': image_id, 'host_name': base_url})


@login_required()
def get_annotations(request, conn=None, **kwargs):
    try:
        fetch_images = strtobool(request.GET.get('fetch_imgs'))
    except (ValueError, AttributeError):
        fetch_images = False
    annotations = tags_data.get_annotations_list(conn, fetch_images)
    return HttpResponse(json.dumps(annotations), content_type='application/json')


@login_required()
def get_tags_by_tagset(request, tagset_id, conn=None, **kwargs):
    try:
        fetch_images = strtobool(request.GET.get('fetch_imgs'))
    except (ValueError, AttributeError):
        fetch_images = False
    logger.debug('"fetch_imgs" value %r', fetch_images)
    tags = tags_data.get_tags_list(tagset_id, conn, fetch_images)
    if tags is None:
        return HttpResponseNotFound("There is no TagSet with ID %s" % tagset_id)
    return HttpResponse(json.dumps(tags), content_type='application/json')


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
def find_images_by_tag(request, tag_id, conn=None, **kwargs):
    images = tags_data.get_images(tag_id, conn)
    return HttpResponse(json.dumps(images), content_type='application/json')


@login_required()
def get_image_dzi(request, image_id, conn=None, **kwargs):
    slide_obj, slides_format = slides_manager.get_deepzoom_metadata(image_id, conn)
    if slide_obj:
        return HttpResponse(slide_obj.get_dzi(slides_format), content_type='application/xml')
    else:
        return HttpResponseNotFound("No image with ID " + image_id)


@login_required()
def get_image_thumbnail(request, image_id, conn=None, **kwargs):
    thumbnail, image_format = slides_manager.get_thumbnail(image_id,
                                                           int(request.GET.get('width')),
                                                           int(request.GET.get('height')),
                                                           conn)
    if thumbnail:
        response = HttpResponse(content_type="image/%s" % image_format)
        thumbnail.save(response, image_format)
        return response
    else:
        return HttpResponseServerError('Unable to load thumbnail')


@login_required()
def get_tile(request, image_id, level, column, row, tile_format, conn=None, **kwargs):
    if tile_format != settings.DEEPZOOM_FORMAT:
        return HttpResponseServerError("Format %s not supported by the server" % tile_format)
    image, image_format = slides_manager.get_tile(image_id, int(level),
                                                  int(column), int(row), conn)
    if image:
        response = HttpResponse(content_type='image/%s' % image_format)
        image.save(response, image_format)
        return response
    else:
        return HttpResponseNotFound("No tile can be found")


@login_required()
def get_image_mpp(request, image_id, conn=None, **kwargs):
    image_mpp = slides_manager.get_image_mpp(image_id, conn)
    return HttpResponse(json.dumps({'image_mpp': image_mpp}), content_type='application_json')
