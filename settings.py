def identity(value):
    return value


CUSTOM_SETTINGS_MAPPINGS = {
    'omero.web.ome_seadragon.search.default_group': ['DEFAULT_SEARCH_GROUP', None, identity, None],
    # configure this value using OMERO.cli
    # <ome_home>/bin/omero config set omero.web.ome_seadragon.repository $(<ome_home>/bin/omero config get omero.data.dir)
    'omero.web.ome_seadragon.repository': ['IMGS_REPOSITORY', None, identity, None],
    'omero.web.ome_seadragon.images_folder': ['IMGS_FOLDER', 'ManagedRepository', identity, None],
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
    'omero.web.ome_seadragon.deepzoom.overlap': ['DEEPZOOM_OVERLAP', 1, identity, None],
    'omero.web.ome_seadragon.deepzoom.format': ['DEEPZOOM_FORMAT', 'jpeg', identity, None],
    'omero.web.ome_seadragon.deepzoom.limit_bounds': ['DEEPZOOM_LIMIT_BOUNDS', True, identity, None],
    'omero.web.ome_seadragon.deepzoom.jpeg_tile_quality': ['DEEPZOOM_JPEG_QUALITY', 90, identity, None],
    'omero.web.ome_seadragon.deepzoom.tile_size': ['DEEPZOOM_TILE_SIZE', 256, identity, None],
    # images cache
    'omero.web.ome_seadragon.images_cache.driver': ['IMAGES_CACHE_DRIVER', None, identity, None],
    # expire time must be expressed with a dictionary with keys
    # days, hours, minutes, seconds
    # missing keys will be set to 0 by default
    'omero.web.ome_seadragon.images_cache.expire_time': ['CACHE_EXPIRE_TIME', None, identity, None],
    # redis config
    'omero.web.ome_seadragon.images_cache.host': ['CACHE_HOST', None, identity, None],
    'omero.web.ome_seadragon.images_cache.port': ['CACHE_PORT', None, identity, None],
    'omero.web.ome_seadragon.images_cache.database': ['CACHE_DB', None, identity, None]
}
