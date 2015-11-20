from abc import ABCMeta, abstractmethod


class CacheInterface(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def _get_tile_key(self, image_id, level, column, row, tile_size, image_format):
        return 'TILE::IMG_%s|L_%s|C_%s-R_%s|S_%spx|F_%s' % (image_id, level, column, row,
                                                            tile_size, image_format.upper())

    @abstractmethod
    def _get_thumbnail_key(self, image_id, image_width, image_height, image_format):
        return 'THUMB::IMG_%s|W_%spx-H_%spx|F_%s' % (image_id, image_width, image_height,
                                                     image_format.upper())

    @abstractmethod
    def tile_to_cache(self, image_id, image_obj, level, column, row, tile_size, image_format):
        pass

    @abstractmethod
    def tile_from_cache(self, image_id, level, column, row, tile_size, image_format):
        pass

    @abstractmethod
    def thumbnail_to_cache(self, image_id, image_obj, image_width, image_height, image_format):
        pass

    @abstractmethod
    def thumbnail_from_cache(self, image_id, image_width, image_height, image_format):
        pass
