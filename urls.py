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
    url(r'^examples/custom_handlers/(?P<image_id>[0-9]+)/$', views.get_example_custom_handlers,
        name='ome_seadragon_test_custom_handlers'),
    # OMERO PROJECTS, DATASETS AND IMAGES
    url(r'^get/projects/$', views.get_projects, name='ome_seadragon_get_projects'),
    url(r'^get/project/(?P<project_id>[0-9]+)/$', views.get_project,
        name='ome_seadragon_get_project'),
    url(r'^get/dataset/(?P<dataset_id>[0-9]+)/$', views.get_dataset,
        name='ome_seadragon_get_dataset'),
    url(r'^get/image/(?P<image_id>[0-9]+)/$', views.get_image,
        name='ome_seadragon_get_image'),
    # OMERO TAGS
    url(r'^get/annotations/$', views.get_annotations,
        name='ome_seadragon_get_annotations'),
    url(r'^get/tagset/(?P<tagset_id>[0-9]+)/$', views.get_tagset,
        name='ome_seadragon_get_tagset'),
    url(r'^get/tag/(?P<tag_id>[0-9]+)/$', views.get_tag,
        name='ome_seadragon_get_tag'),
    url(r'^find/annotations/$', views.find_annotations,
        name='ome_seadragon_find_tags'),
    # DEEPZOOM
    url(r'^deepzoom/get/(?P<image_id>[0-9]+).dzi$', views.get_image_dzi,
        name='ome_seadragon_image_dzi_metadata'),
    url(r'^deepzoom/get/thumbnail/(?P<image_id>[0-9]+).dzi$', views.get_image_thumbnail,
        name='ome_seadragon_image_thumbnail'),
    url(r'^deepzoom/get/(?P<image_id>[0-9]+)_files/(?P<level>[0-9]+)/(?P<column>[0-9]+)_(?P<row>[0-9]+).(?P<tile_format>[\w]+)$',
        views.get_tile, name='ome_seadragon_get_tile'),
    url(r'^deepzoom/image_mpp/(?P<image_id>[0-9]+).dzi$', views.get_image_mpp,
        name='ome_seadragon_get_image_mpp'),
    # 3DHISTECH FILES HANDLING --- DATA MANAGEMENT
    url(r'^mrxs/register_file/$', views.register_original_file, name='ome_seadragon_mrxs_save'),
    url(r'^mrxs/delete_file/(?P<file_name>[\w\-.]+)/$', views.delete_original_file,
        name='ome_seadragon_mrxs_delete_file'),
    url(r'^mrxs/delete_files/(?P<file_name>[\w\-.]+)/$', views.delete_original_files,
        name='ome_seadragon_mrxs_delete_files')
)
