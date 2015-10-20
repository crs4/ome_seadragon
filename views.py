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


@login_required()
def get_tags_list(request, conn=None, **kwargs):
    tags = list()
    for tag in conn.getObjects("TagAnnotation"):
        tags.append({
            "id": tag.getId(),
            "value": tag.getValue(),
            "description": tag.getDescription()
        })
    return HttpResponse(json.dumps(tags), content_type='application/json')


@login_required()
def find_tags(request, conn=None, **kwargs):
    search_pattern = request.GET.get('query')
    qservices = conn.getQueryService()
    qparams = omero.sys.ParametersI()
    qparams.addString('search_pattern', '%%%s%%' % search_pattern)
    query = "SELECT t FROM TagAnnotation t WHERE t.description LIKE :search_pattern OR t.textValue LIKE :search_pattern"
    tags = list()
    for res in qservices.findAllByQuery(query, qparams):
        tags.append({
            "id": res.getId().val,
            "value": res.getTextValue().val,
            "description": res.getDescription().val
        })
    return HttpResponse(json.dumps(tags), content_type='application/json')
