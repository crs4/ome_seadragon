import logging
from distutils.util import strtobool
try:
    import simplejson as json
except ImportError:
    import json

from omeroweb.webclient.decorators import login_required
import omero

from django.http import HttpResponse
from django.shortcuts import render


def check_app(request):
    return HttpResponse("ome_seadragon working!")


logger = logging.getLogger(__name__)


def _get_images_by_tag(tag_id, conn):
    imgs_generator = conn.getObjectsByAnnotations('Image', [tag_id])
    images = list()
    for img in imgs_generator:
        images.append({
            'id': img.getId(),
            'fileset_id': img.getFileset().getId(),
            'name': img.getName()
        })
    return images


@login_required()
def get_tags_list(request, conn=None, **kwargs):
    tags = list()
    try:
        fetch_images = strtobool(request.GET.get('fetch_imgs'))
    except ValueError:
        logger.warn('Unable to cast %s to boolean, forcing false by default', request.GET.get('fetch_imgs'))
        fetch_images = False
    except AttributeError:
        fetch_images = False
    logger.debug('"fetch_imgs" value %r', fetch_images)
    for tag in conn.getObjects("TagAnnotation"):
        imgs_list = list()
        if fetch_images:
            imgs_list = _get_images_by_tag(tag.getId(), conn)
        tags.append({
            "id": tag.getId(),
            "value": tag.getValue(),
            "description": tag.getDescription(),
            "images": imgs_list
        })
    return HttpResponse(json.dumps(tags), content_type='application/json')


@login_required()
def find_tags(request, conn=None, **kwargs):
    search_pattern = request.GET.get('query')
    try:
        fetch_images = strtobool(request.GET.get('fetch_imgs'))
    except ValueError:
        logger.warn('Unable to cast %s to boolean, forcing false by default', request.GET.get('fetch_imgs'))
        fetch_images = False
    except AttributeError:
        fetch_images = False
    logger.debug('"fetch_imgs" value %r', fetch_images)
    qservices = conn.getQueryService()
    qparams = omero.sys.ParametersI()
    qparams.addString('search_pattern', '%%%s%%' % search_pattern)
    query = "SELECT t FROM TagAnnotation t WHERE lower(t.description) LIKE lower(:search_pattern)" \
            " OR lower(t.textValue) LIKE lower(:search_pattern)"
    tags = list()
    for res in qservices.findAllByQuery(query, qparams):
        imgs_list = list()
        if fetch_images:
            imgs_list = _get_images_by_tag(res.getId().val, conn)
        tags.append({
            "id": res.getId().val,
            "value": res.getTextValue().val,
            "description": res.getDescription().val,
            "images": imgs_list
        })
    return HttpResponse(json.dumps(tags), content_type='application/json')


@login_required()
def find_images_by_tag(request, tag_id, conn=None, **kwargs):
    images = _get_images_by_tag(tag_id, conn)
    return HttpResponse(json.dumps(images), content_type='application/json')
