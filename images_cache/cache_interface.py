from ome_seadragon import settings

from abc import ABCMeta, abstractmethod


class CacheInterface(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def _get_tile_key(self, image_id, level, column, row, tile_size, image_format,
                      image_quality=None):
        if image_quality:
            image_format = '%s%s' % (image_format, image_quality)
        return 'TILE::IMG_%s|L_%s|C_%s-R_%s|S_%spx|F_%s|E_%s' % (image_id, level, column, row,
                                                                 tile_size, image_format.upper(),
                                                                 settings.IMAGES_RENDERING_ENGINE)

    @abstractmethod
    def _get_thumbnail_key(self, image_id, thumbnail_size, image_format):
        return 'THUMB::IMG_%s|S_%spx|F_%s|E_%s' % (image_id, thumbnail_size,
                                                   image_format.upper(),
                                                   settings.IMAGES_RENDERING_ENGINE)

    @abstractmethod
    def tile_to_cache(self, image_id, image_obj, level, column, row, tile_size, image_format,
                      image_quality=None):
        pass

    @abstractmethod
    def tile_from_cache(self, image_id, level, column, row, tile_size, image_format,
                        image_quality=None):
        pass

    @abstractmethod
    def thumbnail_to_cache(self, image_id, image_obj, thumbnail_size, image_format):
        pass

    @abstractmethod
    def thumbnail_from_cache(self, image_id, thumbnail_size, image_format):
        pass
