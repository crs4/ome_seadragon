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

class ServerConfigError(Exception):
    pass


def identity(value):
    return value


def int_identity(value):
    return int(value)


def bool_identity(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value == 'True':
            return True
        if value == 'False':
            return False
        raise ValueError('%s can\'t be converted to boolean')
    raise ValueError('Not a bool or a str')

CUSTOM_SETTINGS_MAPPINGS = {
    'omero.web.ome_seadragon.search.default_group': ['DEFAULT_SEARCH_GROUP', None, identity, None],
    # configure this value using OMERO.cli
    # <ome_home>/bin/omero config set omero.web.ome_seadragon.repository $(<ome_home>/bin/omero config get omero.data.dir)
    'omero.web.ome_seadragon.repository': ['IMGS_REPOSITORY', None, identity, None],
    'omero.web.ome_seadragon.images_folder': ['IMGS_FOLDER', 'ManagedRepository', identity, None],
    'omero.web.ome_seadragon.default_mirax_folder': ['MIRAX_FOLDER', None, identity, None],
    # configure this value using OMERO.cli
    # <ome_home>/bin/omero config set omero.web.ome_seadragon.ome_public_user $(<ome_home>/bin/omero config get omero.web.public.user)
    'omero.web.ome_seadragon.ome_public_user': ['OME_PUBLIC_USER', None, identity, None],
    # default rendering engines
    'omero.web.ome_seadragon.tiles.primary_rendering_engine': ['PRIMARY_TILES_RENDERING_ENGINE',
                                                               'openslide', identity, None],
    'omero.web.ome_seadragon.thumbnails.primary_rendering_engine': ['PRIMARY_THUMBNAILS_RENDERING_ENGINE',
                                                                    'omero', identity, None],
    # secondary rendering engines
    'omero.web.ome_seadragon.tiles.secondary_rendering_engine': ['SECONDARY_TILES_RENDERING_ENGINE',
                                                                 'omero', identity, None],
    'omero.web.ome_seadragon.thumbnails.secondary_rendering_engine': ['SECONDARY_THUMBNAILS_RENDERING_ENGINE',
                                                                      'openslide', identity, None],
    # deepzoom properties
    'omero.web.ome_seadragon.deepzoom.overlap': ['DEEPZOOM_OVERLAP', 1, int_identity, None],
    'omero.web.ome_seadragon.deepzoom.format': ['DEEPZOOM_FORMAT', 'jpeg', identity, None],
    'omero.web.ome_seadragon.deepzoom.limit_bounds': ['DEEPZOOM_LIMIT_BOUNDS', True, identity, None],
    'omero.web.ome_seadragon.deepzoom.jpeg_tile_quality': ['DEEPZOOM_JPEG_QUALITY', 90, int_identity, None],
    'omero.web.ome_seadragon.deepzoom.tile_size': ['DEEPZOOM_TILE_SIZE', 256, int_identity, None],
    # images cache
    'omero.web.ome_seadragon.images_cache.cache_enabled': ['IMAGES_CACHE_ENABLED', False, bool_identity, None],
    'omero.web.ome_seadragon.images_cache.driver': ['IMAGES_CACHE_DRIVER', None, identity, None],
    # expire time must be expressed with a dictionary with keys
    # days, hours, minutes, seconds
    # missing keys will be set to 0 by default
    'omero.web.ome_seadragon.images_cache.expire_time': ['CACHE_EXPIRE_TIME', None, identity, None],
    # redis config
    'omero.web.ome_seadragon.images_cache.host': ['CACHE_HOST', None, identity, None],
    'omero.web.ome_seadragon.images_cache.port': ['CACHE_PORT', None, identity, None],
    'omero.web.ome_seadragon.images_cache.database': ['CACHE_DB', None, identity, None],
    # arrays datasets config
    'omero.web.ome_seadragon.dzi_adapter.datasets.repository': ['DATASETS_REPOSITORY', None, identity, None]
}
