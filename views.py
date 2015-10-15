from omeroweb.webclient.decorators import login_required

from django.http import HttpResponse
from django.shortcuts import render


def check_app(request):
    return HttpResponse("ome_seadragon working!")