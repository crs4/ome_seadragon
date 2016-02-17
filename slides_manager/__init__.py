from ome_seadragon import settings


class UnknownRenderingEngine(Exception):
    pass


class RenderingEngineFactory(object):

    def __init__(self):
        self.tiles_rendering_engine = settings.TILES_RENDERING_ENGINE
        self.thumbnails_rendering_engine = settings.THUMBNAILS_RENDERING_ENGINE

    def _get_openslide_engine(self, image_id, connection):
        from openslide_engine import OpenSlideEngine

        return OpenSlideEngine(image_id, connection)

    def _get_omero_engine(self, image_id, connection):
        from ome_engine import OmeEngine

        return OmeEngine(image_id, connection)

    def get_tiles_rendering_engine(self, image_id, connection):
        if self.tiles_rendering_engine == 'openslide':
            return self._get_openslide_engine(image_id, connection)
        if self.tiles_rendering_engine == 'omero':
            return self._get_omero_engine(image_id, connection)
        else:
            raise UnknownRenderingEngine('%s is not a valid rendering engine' % self.tiles_rendering_engine)

    def get_thumbnails_rendering_engine(self, image_id, connection):
        if self.thumbnails_rendering_engine == 'openslide':
            return self._get_openslide_engine(image_id, connection)
        if self.thumbnails_rendering_engine == 'omero':
            return self._get_omero_engine(image_id, connection)
        else:
            raise UnknownRenderingEngine('%s is not a valid rendering engine' % self.thumbnails_rendering_engine)
