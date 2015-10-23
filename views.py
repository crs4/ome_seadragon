from ome_seadragon.ome_data import tags_data
from ome_seadragon import settings

import logging
from distutils.util import strtobool
try:
    import simplejson as json
except ImportError:
    import json

from omeroweb.webclient.decorators import login_required

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render


def check_app(request):
    return HttpResponse("ome_seadragon working!")


def check_repository(request):
    if settings.IMGS_REPOSITORY:
        return HttpResponse(settings.IMGS_REPOSITORY)
    else:
        return HttpResponse("No repository has been configured")


logger = logging.getLogger(__name__)


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
