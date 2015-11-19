import logging
import os
import openslide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator
from io import BytesIO

from ome_seadragon import settings


logger = logging.getLogger(__name__)


class PilBytesIO(BytesIO):
    def fileno(self, *args, **kwargs):
        raise AttributeError("Not supported")


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
    image_path = _get_image_path(image_id, conn)
    if image_path:
        slide = OpenSlide(image_path)
        thumbnail = slide.get_thumbnail((width, height))
    else:
        thumbnail = None
    return thumbnail, settings.DEEPZOOM_FORMAT


def get_tile(image_id, level, column, row, conn):
    image_path = _get_image_path(image_id, conn)
    if image_path:
        slide = _get_slide(image_path)
        tile = slide.get_tile(level, (column, row))
        img_buffer = PilBytesIO()
        tile_conf = {
            'format': settings.DEEPZOOM_FORMAT
        }
        if settings.DEEPZOOM_FORMAT == 'jpeg':
            tile_conf['quality'] = settings.DEEPZOOM_JPEG_COMPRESSION
        tile.save(img_buffer, **tile_conf)
        return img_buffer, 'image/%s' % settings.DEEPZOOM_FORMAT
    else:
        return None, 'image/%s' % settings.DEEPZOOM_FORMAT
