from django.conf.urls import *
from ome_seadragon import views

urlpatterns = patterns('django.views.generic.simple',

                       url(r'^test/$', views.check_app, name='ome_seadragon_test'),
                       )