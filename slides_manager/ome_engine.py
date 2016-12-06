import math
from lxml import etree
from PIL import Image
from cStringIO import StringIO

from errors import UnsupportedSource

from ome_seadragon.ome_data.projects_datasets import get_fileset_highest_resolution
from rendering_engine_interface import RenderingEngineInterface
from ome_seadragon import settings
from ome_seadragon.images_cache import CacheDriverFactory


class OmeEngine(RenderingEngineInterface):

    def __init__(self, image_id, connection):
        super(OmeEngine, self).__init__(image_id, connection)

    # if get_biggest_in_filest is True, return the image with the highest resolution in the fileset
    # of the image with ID image_id, if False simply return image with ID image_id
    def _get_image_object(self, get_biggest_in_fileset=True):
        img = self.connection.getObject('Image', self.image_id)
        if img is None:
            return None
        if get_biggest_in_fileset:
            return get_fileset_highest_resolution(img, self.connection)
        else:
            return img

    def _get_dzi_max_level(self, img=None):
        if img is None:
            img = self._get_image_object()
        x = img.getSizeX()
        y = img.getSizeY()
        return int(math.ceil(math.log(max(x, y), 2)))

    def _get_dzi_scale_factor(self, level, img=None):
        max_level = self._get_dzi_max_level(img)
        if level > max_level:
            raise ValueError('Level %d is higher than max DZI level for the image' % level)
        return math.pow(0.5, max_level - level)

    def _get_ome_scale_map(self, img=None, swap_keys=False):
        if img is None:
            img = self._get_image_object()
        tmp_map = img.getZoomLevelScaling()
        ome_scale_map = dict((len(tmp_map) - k - 1, v) for k, v in tmp_map.iteritems())
        if not swap_keys:
            return ome_scale_map
        else:
            return dict((v, k) for k, v in ome_scale_map.iteritems())

    def _get_ome_scale_factor(self, level, img=None):
        return self._get_ome_scale_map(img)[level]

    def _get_best_downscale_level(self, level, img_obj=None):
        ome_scale_map = self._get_ome_scale_map(img_obj, swap_keys=True)
        dzi_scale_factor = self._get_dzi_scale_factor(level, img_obj)
        for ome_scale_factor, ome_level in sorted(ome_scale_map.iteritems(), reverse=True):
            if ome_scale_factor < dzi_scale_factor:
                return ome_level + 1
        return ome_level

    def _get_scale_factor(self, original_x, original_y, ome_scale_factor, dzi_scale_factor):
        ome_w = original_x * ome_scale_factor
        ome_h = original_y * ome_scale_factor
        ome_diag = math.sqrt(math.pow(ome_w, 2) + math.pow(ome_h, 2))
        dzi_w = original_x * dzi_scale_factor
        dzi_h = original_y * dzi_scale_factor
        dzi_diag = math.sqrt(math.pow(dzi_w, 2) + math.pow(dzi_h, 2))
        return ome_diag / dzi_diag

    def _get_ome_tile(self, ome_img, ome_level, dzi_level, column, row):
        scale_factor = self._get_scale_factor(ome_img.getSizeX(), ome_img.getSizeY(),
                                              self._get_ome_scale_factor(ome_level, ome_img),
                                              self._get_dzi_scale_factor(dzi_level, ome_img))
        ome_tile_size = (settings.DEEPZOOM_TILE_SIZE + 2 * settings.DEEPZOOM_OVERLAP) * scale_factor
        ome_x = row * (settings.DEEPZOOM_TILE_SIZE * scale_factor)
        if ome_x != 0:
            ome_x -= settings.DEEPZOOM_OVERLAP * scale_factor
        ome_y = column * (settings.DEEPZOOM_TILE_SIZE * scale_factor)
        if ome_y != 0:
            ome_y -= settings.DEEPZOOM_OVERLAP * scale_factor
        if ome_x == 0 or (ome_x + ome_tile_size >= ome_img.getSizeX()):
            ome_tile_size_x = ome_tile_size - (settings.DEEPZOOM_OVERLAP * scale_factor)
        else:
            ome_tile_size_x = ome_tile_size
        if ome_y == 0 or (ome_y + ome_tile_size >= ome_img.getSizeY()):
            ome_tile_size_y = ome_tile_size - (settings.DEEPZOOM_OVERLAP * scale_factor)
        else:
            ome_tile_size_y = ome_tile_size
        # right now, we don't handle Z and T levels
        self.logger.debug('Getting tile with settings: X %s Y %s W %s H %s L %s', ome_x, ome_y,
                          ome_tile_size_x, ome_tile_size_y, ome_level)
        try:
            tile_buffer = StringIO(ome_img.renderJpegRegion(0, 0, ome_x, ome_y, ome_tile_size_x,
                                                            ome_tile_size_y, level=ome_level,
                                                            compression=settings.DEEPZOOM_JPEG_QUALITY/100.0))
            ome_tile = Image.open(tile_buffer)
            tile_w, tile_h = ome_tile.size
            if scale_factor != 1:
                self.logger.debug('Scale factor is %s resize tile', scale_factor)
                tile = ome_tile.resize((int(round(tile_w / scale_factor)),
                                        int(round(tile_h / scale_factor))),
                                       Image.ANTIALIAS)
            else:
                tile = ome_tile
            return tile
        except TypeError:
            # return a white tile
            return Image.new('RGB', (settings.DEEPZOOM_TILE_SIZE, settings.DEEPZOOM_TILE_SIZE), 'white')

    def _get_image_mpp(self, original_file_source=False):
        img = self._get_image_object(original_file_source)
        if img:
            try:
                mpp = (img.getPixelSizeX() + img.getPixelSizeY()) / 2.0
            except TypeError:
                mpp = 0
        else:
            mpp = 0
        return mpp

    def _check_source_type(self, original_file_source):
        if original_file_source:
            raise UnsupportedSource('OMERO rendering engine does not support OriginalFile as source')

    def get_openseadragon_config(self, original_file_source=False, file_mimetype=None):
        self._check_source_type(original_file_source)
        return {
            'mpp': self._get_image_mpp()
        }

    def get_dzi_description(self, original_file_source=False, file_mimetype=None):
        self._check_source_type(original_file_source)
        img = self._get_image_object(original_file_source)
        if img:
            dzi_root = etree.Element(
                'Image',
                attrib={
                    'Format': str(settings.DEEPZOOM_FORMAT),
                    'Overlap': str(settings.DEEPZOOM_OVERLAP),
                    'TileSize': str(settings.DEEPZOOM_TILE_SIZE)
                },
                nsmap={None: 'http://schemas.microsoft.com/deepzoom/2008'}
            )
            etree.SubElement(dzi_root, 'Size',
                             attrib={'Height': str(img.getSizeY()), 'Width': str(img.getSizeX())})
            return etree.tostring(dzi_root)
        else:
            return None

    def get_thumbnail(self, size, original_file_source=False, file_mimeype=None):
        self._check_source_type(original_file_source)
        cache = CacheDriverFactory().get_cache('omero')
        thumbnail = cache.thumbnail_from_cache(self.image_id, size,
                                               settings.DEEPZOOM_FORMAT)
        if thumbnail is None:
            self.logger.info('No thumbnail loaded from cache, building it')
            # we want the thumbnail of the image, not the one of the highest resolution image in fileset
            ome_img = self._get_image_object(get_biggest_in_fileset=False)
            if ome_img:
                if ome_img.getSizeX() >= ome_img.getSizeY():
                    th_size = (size, )
                else:
                    th_w = size * (float(ome_img.getSizeX()) / ome_img.getSizeY())
                    th_size = (th_w, size)
                thumbnail_buffer = StringIO(ome_img.getThumbnail(size=th_size))
                thumbnail = Image.open(thumbnail_buffer)
                cache.thumbnail_to_cache(self.image_id, thumbnail, size,
                                         settings.DEEPZOOM_FORMAT)
        else:
            self.logger.info('Thumbnail loaded from cache')
        return thumbnail, settings.DEEPZOOM_FORMAT

    def get_tile(self, level, column, row, original_file_source=False, file_mimetype=None):
        self._check_source_type(original_file_source)
        cache = CacheDriverFactory().get_cache('omero')
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
        tile = cache.tile_from_cache(**cache_params)
        if tile is None:
            ome_img = self._get_image_object()
            ome_level = self._get_best_downscale_level(level, ome_img)
            tile = self._get_ome_tile(ome_img, ome_level, level, row=column, column=row)
            cache_params['image_obj'] = tile
            cache.tile_to_cache(**cache_params)
        return tile, settings.DEEPZOOM_FORMAT
