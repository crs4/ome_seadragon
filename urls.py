from django.conf.urls import *
from ome_seadragon import views

urlpatterns = patterns(
    'django.views.generic.simple',
    # TEST
    url(r'^test/$', views.check_app, name='ome_seadragon_test'),
    # OMERO TAGS
    url(r'^get/annotations/$', views.get_annotations,
        name='ome_seadragon_get_annotations'),
    url(r'^get/tags/(?P<tagset_id>[0-9]+)/$', views.get_tags_by_tagset,
        name='ome_seadragon_get_tags_by_tagset'),
    url(r'^find/annotations/$', views.find_annotations,
        name='ome_seadragon_find_tags'),
    url(r'^get/imgs_by_tag/(?P<tag_id>[0-9]+)/$', views.find_images_by_tag,
        name='ome_seadragon_find_images_by_tag'),
)
