import openslide
from openslide import OpenSlide
from openslide.deepzoom import DeepZoomGenerator
from cStringIO import StringIO
from PIL import Image

from rendering_engine_interface import RenderingEngineInterface
from ome_seadragon import settings
from ome_seadragon.images_cache import CacheDriverFactory


class OpenSlideEngine(RenderingEngineInterface):

    def __init__(self, image_id, connection):
        super(OpenSlideEngine, self).__init__(image_id, connection)

    def _get_openslide_wrapper(self):
        img_path = self._get_image_path()
        if img_path:
            return OpenSlide(img_path)
        else:
            return None

    def _get_deepzoom_config(self):
        return {
            'tile_size': settings.DEEPZOOM_TILE_SIZE,
            'overlap': settings.DEEPZOOM_OVERLAP,
            'limit_bounds': settings.DEEPZOOM_LIMIT_BOUNDS
        }

    def _get_deepzoom_wrapper(self):
        os_wrapper = self._get_openslide_wrapper()
        if os_wrapper:
            return DeepZoomGenerator(os_wrapper, **self._get_deepzoom_config())
        else:
            return None

    def _get_image_mpp(self):
        slide = self._get_openslide_wrapper()
        if slide:
            try:
                mpp_x = slide.properties[openslide.PROPERTY_NAME_MPP_X]
                mpp_y = slide.properties[openslide.PROPERTY_NAME_MPP_Y]
                return (float(mpp_x) + float(mpp_y)) / 2
            except (KeyError, ValueError):
                return 0
        else:
            return 0

    def get_openseadragon_config(self):
        return {
            'mpp': self._get_image_mpp()
        }

    def get_dzi_description(self):
        dzi_slide = self._get_deepzoom_wrapper()
        if dzi_slide:
            return dzi_slide.get_dzi(settings.DEEPZOOM_FORMAT)
        else:
            return None

    def get_thumbnail(self, size):
        cache = CacheDriverFactory().get_cache()
        # get thumbnail from cache
        thumb = cache.thumbnail_from_cache(self.image_id, size,
                                           settings.DEEPZOOM_FORMAT)
        # if thumbnail is not in cache build it ....
        if thumb is None:
            self.logger.info('No thumbnail loaded from cache, building it')
            slide = self._get_openslide_wrapper()
            if slide:
                thumb = slide.get_thumbnail((size, size))
                # ... and store it into the cache
                cache.thumbnail_to_cache(self.image_id, thumb, size,
                                         settings.DEEPZOOM_FORMAT)
        else:
            self.logger.info('Thumbnail loaded from cache')
        return thumb, settings.DEEPZOOM_FORMAT

    def get_tile(self, level, column, row):
        cache = CacheDriverFactory().get_cache()
        cache_params = {
            'image_id': self.image_id,
            'level': level,
            'column': column,
            'row': row,
            'tile_size': settings.DEEPZOOM_TILE_SIZE,
            'image_format': settings.DEEPZOOM_FORMAT
        }
        if cache_params['image_format'].lower() == 'jpeg':
            cache_params['image_quality'] = settings.DEEPZOOM_JPEG_QUALITY
        # get tile from cache
        tile = cache.tile_from_cache(**cache_params)
        # if tile is not in cache build id ...
        if tile is None:
            img_path = self._get_image_path()
            if img_path:
                slide = self._get_deepzoom_wrapper()
                dzi_tile = slide.get_tile(level, (column, row))
                tile_buffer = StringIO()
                tile_conf = {
                    'format': settings.DEEPZOOM_FORMAT
                }
                if tile_conf['format'].lower() == 'jpeg':
                    tile_conf['quality'] = settings.DEEPZOOM_JPEG_QUALITY
                dzi_tile.save(tile_buffer, **tile_conf)
                tile = Image.open(tile_buffer)
                # ... and store it into the cache
                cache_params['image_obj'] = tile
                cache.tile_to_cache(**cache_params)
        return tile, settings.DEEPZOOM_FORMAT