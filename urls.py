from django.conf.urls import *
from ome_seadragon import views

urlpatterns = patterns(
    'django.views.generic.simple',
    # TEST
    url(r'^test/$', views.check_app, name='ome_seadragon_test'),
    url(r'test/repository/$', views.check_repository, name='ome_seadragon_test_repository'),
    url(r'test/repository/(?P<image_id>[0-9]+)/$', views.check_image_path,
        name='ome_seadragon_test_image_path'),
    # EXAMPLES
    url(r'^examples/viewer/(?P<image_id>[0-9]+)/$', views.get_example_viewer,
        name='ome_seadragon_test_viewer'),
    url(r'^examples/annotations/(?P<image_id>[0-9]+)/$', views.get_example_annotations,
        name='ome_seadragon_test_annotations'),
    url(r'^examples/ome_rois/(?P<image_id>[0-9]+)/$', views.get_example_ome_rois,
        name='ome_seadragon_test_ome_rois'),
    # OMERO TAGS
    url(r'^get/annotations/$', views.get_annotations,
        name='ome_seadragon_get_annotations'),
    url(r'^get/tags/(?P<tagset_id>[0-9]+)/$', views.get_tags_by_tagset,
        name='ome_seadragon_get_tags_by_tagset'),
    url(r'^find/annotations/$', views.find_annotations,
        name='ome_seadragon_find_tags'),
    url(r'^get/imgs_by_tag/(?P<tag_id>[0-9]+)/$', views.find_images_by_tag,
        name='ome_seadragon_find_images_by_tag'),
    # DEEPZOOM
    url(r'^deepzoom/get/(?P<image_id>[0-9]+).dzi$', views.get_image_dzi,
        name='ome_seadragon_image_dzi_metadata'),
    url(r'^deepzoom/get/thumbnail/(?P<image_id>[0-9]+).dzi$', views.get_image_thumbnail,
        name='ome_seadragon_image_thumbnail'),
    url(r'^deepzoom/get/(?P<image_id>[0-9]+)_files/(?P<level>[0-9]+)/(?P<column>[0-9]+)_(?P<row>[0-9]+).(?P<tile_format>[\w]+)$',
        views.get_tile, name='ome_seadragon_get_tile'),
    url(r'^deepzoom/image_mpp/(?P<image_id>[0-9]).dzi$', views.get_image_mpp,
        name='ome_seadragon_get_image_mpp')
)
