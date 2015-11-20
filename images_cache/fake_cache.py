from cache_interface import CacheInterface


class FakeCache(CacheInterface):

    def __init__(self):
        pass

    def _get_tile_key(self, image_id, level, column, row, tile_size, image_format):
        pass

    def _get_thumbnail_key(self, image_id, image_width, image_height, image_format):
        pass

    def tile_to_cache(self, image_id, image_obj, level, column, row, tile_size, image_format):
        pass

    def tile_from_cache(self, image_id, level, column, row, tile_size, image_format):
        return None

    def thumbnail_to_cache(self, image_id, image_obj, image_width, image_height, image_format):
        pass

    def thumbnail_from_cache(self, image_id, image_width, image_height, image_format):
        return None
