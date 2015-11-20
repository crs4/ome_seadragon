from ome_seadragon import settings


class CacheDriverFactory(object):

    def __init__(self):
        self.cache_driver = settings.IMAGES_CACHE_DRIVER

    def _get_redis_driver(self):
        from redis_img_cache import RedisCache

        return RedisCache(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB,
                          settings.CACHE_EXPIRE_TIME)

    def get_cache(self):
        if self.cache_driver == 'redis':
            return self._get_redis_driver()
        else:
            return None
