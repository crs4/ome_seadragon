from ome_seadragon import settings


class UnknownCacheDriver(Exception):
    pass


class CacheDriverFactory(object):

    def __init__(self):
        self.cache_driver = settings.IMAGES_CACHE_DRIVER

    def _get_fake_cache(self):
        from fake_cache import FakeCache

        return FakeCache()

    def _get_redis_driver(self):
        from redis_img_cache import RedisCache

        return RedisCache(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB,
                          settings.CACHE_EXPIRE_TIME)

    def get_cache(self):
        if not settings.IMAGES_CACHE_ENABLED:
            return self._get_fake_cache()
        else:
            if self.cache_driver == 'redis':
                return self._get_redis_driver()
            else:
                raise UnknownCacheDriver('There is no driver for %s' % self.cache_driver)
