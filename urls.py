#  Copyright (c) 2019, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from django.conf.urls import *
from ome_seadragon import views

urlpatterns = patterns(
    'django.views.generic.simple',
    # INITIALIZE SESSION
    url(r'connect/$', views.start_connection, name='ome_seadragon_connect'),
    # TEST
    url(r'^test/$', views.check_app, name='ome_seadragon_test'),
    url(r'test/repository/$', views.check_repository, name='ome_seadragon_test_repository'),
    url(r'test/repository/(?P<image_id>[0-9]+)/$', views.check_image_path,
        name='ome_seadragon_test_image_path'),
    # EXAMPLES
    url(r'^examples/viewer/(?P<image_id>[\w\-.]+)/$', views.get_example_viewer,
        name='ome_seadragon_test_viewer'),
    url(r'^examples/viewer_json/(?P<image_id>[\w\-.]+)/$', views.get_example_viewer_json,
        name='ome_seadragon_test_viewer_json'),
    url(r'^examples/sequence_viewer/(?P<dataset_id>[0-9]+)/$', views.get_example_sequence_viewer,
        name='ome_seadragon_test_sequence_viewer'),
    url(r'^examples/double_viewer/(?P<image_a_id>[\w\-.]+)_(?P<image_b_id>[\w\-.]+)/$', 
        views.get_example_double_viewer, name='ome_seadragon_test_double_viewer'),
    url(r'^examples/annotations/(?P<image_id>[\w\-.]+)/$', views.get_example_annotations,
        name='ome_seadragon_test_annotations'),
    url(r'^examples/ome_rois/(?P<image_id>[0-9]+)/$', views.get_example_ome_rois,
        name='ome_seadragon_test_ome_rois'),
    url(r'^examples/custom_handlers/markers/(?P<image_id>[\w\-.]+)/$',
        views.get_example_interactive_markers,
        name='ome_seadragon_test_interactive_markers'),
    url(r'^examples/custom_handlers/polygons/(?P<image_id>[\w\-.]+)/$',
        views.get_example_interactive_polygons,
        name='ome_seadragon_test_interactive_polygons'),
    url(r'^examples/custom_handlers/rulers/(?P<image_id>[\w\-.]+)/$',
        views.get_example_interactive_rulers,
        name='ome_seadragon_test_interactive_rulers'),
    url(r'^examples/custom_handlers/freehand/(?P<image_id>[\w\-.]+)/$',
        views.get_example_interactive_freehand),
    # OMERO PROJECTS, DATASETS AND IMAGES
    url(r'^get/projects/$', views.get_projects, name='ome_seadragon_get_projects'),
    url(r'^get/project/(?P<project_id>[0-9]+)/$', views.get_project,
        name='ome_seadragon_get_project'),
    url(r'^get/dataset/(?P<dataset_id>[0-9]+)/$', views.get_dataset,
        name='ome_seadragon_get_dataset'),
    url(r'^get/image/(?P<image_id>[0-9]+)/$', views.get_image,
        name='ome_seadragon_get_image'),
    url(r'^get/images/index/$', views.get_images_quick_list,
        name='ome_seadragon_get_images_index'),
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
    url(r'^deepzoom/get/(?P<image_id>[0-9]+).json$', views.get_image_json,
        name='ome_seadragon_image_json_metadata'),
    url(r'^deepzoom/get/(?P<image_id>[0-9]+)_metadata.json$', views.get_image_metadata,
        name='ome_seadragon_image_json_metadata_full'),
    url(r'^deepzoom/get/thumbnail/(?P<image_id>[0-9]+).dzi$', views.get_image_thumbnail,
        name='ome_seadragon_image_thumbnail'),
    url(r'^deepzoom/get/(?P<image_id>[0-9]+)_files/(?P<level>[0-9]+)/'
        r'(?P<column>[0-9]+)_(?P<row>[0-9]+).(?P<tile_format>[\w]+)$',
        views.get_tile, name='ome_seadragon_get_tile'),
    url(r'^deepzoom/image_mpp/(?P<image_id>[0-9]+).dzi$', views.get_image_mpp,
        name='ome_seadragon_get_image_mpp'),
    url(r'^deepzoom/slide_bounds/(?P<image_id>[0-9]+).dzi$', views.get_slide_bounds,
        name='ome_seadragon_get_slide_bounds'),
    # 3DHISTECH FILES HANDLING --- DATA MANAGEMENT
    url(r'^mirax/register_file/$', views.register_original_file, name='ome_seadragon_mrxs_save'),
    url(r'^mirax/file_info/(?P<file_name>[\w\-.]+)/$', views.get_original_file_infos,
        name='ome_seadragon_mrxs_file_info'),
    url(r'^mirax/delete_file/(?P<file_name>[\w\-.]+)/$', views.delete_original_file,
        name='ome_seadragon_mrxs_delete_file'),
    url(r'^mirax/delete_files/(?P<file_name>[\w\-.]+)/$', views.delete_original_files,
        name='ome_seadragon_mrxs_delete_files'),
    # 3DHISTECH FILES HANDLING --- DEEPZOOM
    url(r'^mirax/deepzoom/get/(?P<image_id>[\w\-.]+).dzi$', views.get_image_dzi,
        name='ome_seadragon_image_dzi_metadata_mrxs',
        kwargs={'fetch_original_file': True, 'file_mimetype': 'mirax/index'}),
    url(r'^mirax/deepzoom/get/(?P<image_id>[\w\-.]+)_metadata.json$', views.get_image_metadata,
        name='ome_seadragon_image_json_metadata_full',
        kwargs={'fetch_original_file': True, 'file_mimetype': 'mirax/index'}),
    url(r'^mirax/deepzoom/get/(?P<image_id>[\w\-.]+).json$', views.get_image_json,
        name='ome_seadragon_image_json_metadata_mrxs',
        kwargs={'fetch_original_file': True, 'file_mimetype': 'mirax/index'}),
    url(r'^mirax/deepzoom/get/thumbnail/(?P<image_id>[\w\-.]+).dzi$', views.get_image_thumbnail,
        name='ome_seadragon_image_thumbnail_mrxs',
        kwargs={'fetch_original_file': True, 'file_mimetype': 'mirax/index'}),
    url(r'^mirax/deepzoom/get/(?P<image_id>[\w\-.]+)_files/(?P<level>[0-9]+)/'
        r'(?P<column>[0-9]+)_(?P<row>[0-9]+).(?P<tile_format>[\w]+)$',
        views.get_tile, name='ome_seadragon_get_tile_mrxs',
        kwargs={'fetch_original_file': True, 'file_mimetype': 'mirax/index'}),
    url(r'^mirax/deepzoom/image_mpp/(?P<image_id>[\w\-.]+).dzi$', views.get_image_mpp,
        name='ome_seadragon_get_image_mpp_mrxs',
        kwargs={'fetch_original_file': True, 'file_mimetype': 'mirax/index'}),
    url(r'^mirax/deepzoom/slide_bounds/(?P<image_id>[\w\-.]+).dzi$', views.get_slide_bounds,
        name='ome_seadragon_get_slide_bounds',
        kwargs={'fetch_original_file': True, 'file_mimetype': 'mirax/index'})
)
