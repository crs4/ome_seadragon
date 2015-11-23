import logging
import os
import openslide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator
from cStringIO import StringIO
from PIL import Image

from ome_seadragon import settings
from ome_seadragon.images_cache import CacheDriverFactory


logger = logging.getLogger(__name__)


def _get_image_path(image_id, conn):
    img = conn.getObject("Image", image_id)
    if img is None:
        return None
    else:
        return os.path.join(settings.IMGS_REPOSITORY, settings.IMGS_FOLDER,
                            img.getImportedImageFilePaths()['server_paths'][0])


def _get_deepzoom_slide_config():
    return {
        'tile_size': settings.DEEPZOOM_TILE_SIZE,
        'overlap': settings.DEEPZOOM_OVERLAP,
        'limit_bounds': settings.DEEPZOOM_LIMIT_BOUNDS
    }


def _get_slide(image_path):
    oslide_ref = OpenSlide(image_path)
    slide = DeepZoomGenerator(oslide_ref, **_get_deepzoom_slide_config())
    try:
        mpp_x = oslide_ref.properties[openslide.PROPERTY_NAME_MPP_X]
        mpp_y = oslide_ref.properties[openslide.PROPERTY_NAME_MPP_Y]
        slide.mpp = (float(mpp_x) + float(mpp_y)) / 2
    except (KeyError, ValueError):
        slide.mpp = 0
    return slide


def get_deepzoom_metadata(image_id, conn):
    image_path = _get_image_path(image_id, conn)
    if image_path:
        slide = _get_slide(image_path)
        return slide, settings.DEEPZOOM_FORMAT
    else:
        return None, settings.DEEPZOOM_FORMAT


def get_image_mpp(image_id, conn):
    image_path = _get_image_path(image_id, conn)
    if image_path:
        slide = OpenSlide(image_path)
        try:
            mpp_x = slide.properties[openslide.PROPERTY_NAME_MPP_X]
            mpp_y = slide.properties[openslide.PROPERTY_NAME_MPP_Y]
            return (float(mpp_x) + float(mpp_y)) / 2
        except (KeyError, ValueError):
            return 0


def get_thumbnail(image_id, width, height, conn):
    cache_factory = CacheDriverFactory()
    cache = cache_factory.get_cache()
    # get thumbnail from cache
    thumbnail = cache.thumbnail_from_cache(image_id, width, height,
                                           settings.DEEPZOOM_FORMAT)
    # if thumbnail is not in cache build it...
    if thumbnail is None:
        logger.info('No item loaded from cache, building it')
        image_path = _get_image_path(image_id, conn)
        if image_path:
            slide = OpenSlide(image_path)
            thumbnail = slide.get_thumbnail((width, height))
            # ... and store it to cache
            cache.thumbnail_to_cache(image_id, thumbnail, width, height,
                                     settings.DEEPZOOM_FORMAT)
        else:
            thumbnail = None
    else:
        logger.info('Thumbnail loaded from cache')
    return thumbnail, settings.DEEPZOOM_FORMAT


def get_tile(image_id, level, column, row, conn):
    cache_factory = CacheDriverFactory()
    cache = cache_factory.get_cache()
    # configure cache callback
    cache_callback_params = {
        'image_id': image_id,
        'level': level,
        'column': column,
        'row': row,
        'tile_size': settings.DEEPZOOM_TILE_SIZE,
        'image_format': settings.DEEPZOOM_FORMAT
    }
    if settings.DEEPZOOM_FORMAT.lower() == 'jpeg':
        cache_callback_params['image_compression'] = settings.DEEPZOOM_JPEG_QUALITY
    image = cache.tile_from_cache(**cache_callback_params)
    # if tile is not in cache build it...
    if image is None:
        image_path = _get_image_path(image_id, conn)
        if image_path:
            slide = _get_slide(image_path)
            tile = slide.get_tile(level, (column, row))
            img_buffer = StringIO()
            tile_conf = {
                'format': settings.DEEPZOOM_FORMAT
            }
            if settings.DEEPZOOM_FORMAT == 'jpeg':
                tile_conf['quality'] = settings.DEEPZOOM_JPEG_QUALITY
            tile.save(img_buffer, **tile_conf)
            image = Image.open(img_buffer)
            # ... and store it to cache
            cache_callback_params['image_obj'] = image
            cache.tile_to_cache(**cache_callback_params)
    return image, settings.DEEPZOOM_FORMAT
