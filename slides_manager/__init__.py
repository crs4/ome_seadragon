from ome_seadragon import settings


class UnknownRenderingEngine(Exception):
    pass


class RenderingEngineFactory(object):

    def __init__(self):
        self.primary_tiles_rendering_engine = settings.PRIMARY_TILES_RENDERING_ENGINE
        self.primary_thumbnails_rendering_engine = settings.PRIMARY_THUMBNAILS_RENDERING_ENGINE
        try:
            self.secondary_tiles_rendering_engine = settings.SECONDARY_TILES_RENDERING_ENGINE
        except AttributeError:
            self.secondary_tiles_rendering_engine = None
        try:
            self.secondary_thumbnails_rendering_engine = settings.SECONDARY_THUMBNAILS_RENDERING_ENGINE
        except AttributeError:
            self.secondary_thumbnails_rendering_engine = None

    def _get_openslide_engine(self, image_id, connection):
        from openslide_engine import OpenSlideEngine

        return OpenSlideEngine(image_id, connection)

    def _get_omero_engine(self, image_id, connection):
        from ome_engine import OmeEngine

        return OmeEngine(image_id, connection)

    def _get_engine(self, engine, image_id, connection):
        if engine == 'openslide':
            return self._get_openslide_engine(image_id, connection)
        if engine == 'omero':
            return self._get_omero_engine(image_id, connection)
        else:
            raise UnknownRenderingEngine('%s is not a valid rendering engine' % self.primary_thumbnails_rendering_engine)

    def get_primary_tiles_rendering_engine(self, image_id, connection):
        return self._get_engine(self.primary_tiles_rendering_engine, image_id, connection)

    def get_primary_thumbnails_rendering_engine(self, image_id, connection):
        return self._get_engine(self.primary_thumbnails_rendering_engine, image_id, connection)

    def get_secondary_tiles_rendering_engine(self, image_id, connection):
        if self.secondary_tiles_rendering_engine:
            return self._get_engine(self.secondary_tiles_rendering_engine, image_id, connection)
        else:
            return None

    def get_secondary_thumbnails_rendering_engine(self, image_id, connection):
        if self.secondary_thumbnails_rendering_engine:
            return self._get_engine(self.secondary_thumbnails_rendering_engine, image_id, connection)
        else:
            return None
