try:
    import simplejson as json
except ImportError:
    import json


def identity(value):
    return value


def time_dict_to_seconds(value):
    time_conf = json.loads(value)
    days_to_seconds = time_conf.get('days', 0) * 24 * 60 * 60
    hours_to_seconds = time_conf.get('hours', 0) * 60 * 60
    minutes_to_seconds = time_conf.get('minutes', 0) * 60
    return days_to_seconds + hours_to_seconds + minutes_to_seconds + time_conf.get('seconds', 0)

CUSTOM_SETTINGS_MAPPINGS = {
    'omero.web.ome_seadragon.search.default_group': ['DEFAULT_SEARCH_GROUP', None, identity, None],
    # configure this value using OMERO.cli
    # <ome_home>/bin/omero config set omero.web.ome_seadragon.repository $(<ome_home>/bin/omero config get omero.data.dir)
    'omero.web.ome_seadragon.repository': ['IMGS_REPOSITORY', None, identity, None],
    'omero.web.ome_seadragon.images_folder': ['IMGS_FOLDER', 'ManagedRepository', identity, None],
    # default rendering engine
    'omero.web.ome_seadragon.rendering_engine': ['IMAGES_RENDERING_ENGINE', 'openslide', identity, None],
    # deepzoom properties
    'omero.web.ome_seadragon.deepzoom.overlap': ['DEEPZOOM_OVERLAP', 1, identity, None],
    'omero.web.ome_seadragon.deepzoom.format': ['DEEPZOOM_FORMAT', 'jpeg', identity, None],
    'omero.web.ome_seadragon.deepzoom.limit_bounds': ['DEEPZOOM_LIMIT_BOUNDS', True, identity, None],
    'omero.web.ome_seadragon.deepzoom.jpeg_tile_quality': ['DEEPZOOM_JPEG_QUALITY', 90, identity, None],
    'omero.web.ome_seadragon.deepzoom.tile_size': ['DEEPZOOM_TILE_SIZE', 256, identity, None],
    # images cache
    'omero.web.ome_seadragon.images_cache.cache_enabled': ['IMAGES_CACHE_ENABLED', False, identity, None],
    'omero.web.ome_seadragon.images_cache.driver': ['IMAGES_CACHE_DRIVER', 'redis', identity, None],
    # expire time must be expressed with a dictionary with keys
    # days, hours, minutes, seconds
    # missing keys will be set to 0 by default
    'omero.web.ome_seadragon.images_cache.expire_time': ['CACHE_EXPIRE_TIME', '{"minutes": 15}',
                                                         time_dict_to_seconds, None],
    # redis config
    'omero.web.ome_seadragon.images_cache.redis.host': ['REDIS_HOST', 'localhost', identity, None],
    'omero.web.ome_seadragon.images_cache.redis.port': ['REDIS_PORT', 6379, identity, None],
    'omero.web.ome_seadragon.images_cache.redis.database': ['REDIS_DB', 0, identity, None]
}
