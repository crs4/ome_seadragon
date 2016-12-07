from cache_interface import CacheInterface


class FakeCache(CacheInterface):

    def __init__(self):
        pass

    def _get_tile_key(self, engine, image_id, level, column, row, tile_size, image_format,
                      image_quality=None):
        pass

    def _get_thumbnail_key(self, engine, image_id, thumbnail_size, image_format):
        pass

    def tile_to_cache(self, image_id, image_obj, level, column, row, tile_size, image_format,
                      image_quality=None):
        pass

    def tile_from_cache(self, image_id, level, column, row, tile_size, image_format,
                        image_quality=None):
        return None

    def thumbnail_to_cache(self, image_id, image_obj, thumbnail_size, image_format):
        pass

    def thumbnail_from_cache(self, image_id, thumbnail_size, image_format):
        return None
