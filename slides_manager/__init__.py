from ome_seadragon import settings


class UnknownRenderingEngine(Exception):
    pass


class RenderingEngineFactory(object):

    def __init__(self):
        self.rendering_engine = settings.IMAGES_RENDERING_ENGINE

    def _get_openslide_engine(self, image_id, connection):
        from openslide_engine import OpenSlideEngine

        return OpenSlideEngine(image_id, connection)

    def _get_omero_engine(self, image_id, connection):
        from ome_engine import OmeEngine

        return OmeEngine(image_id, connection)

    def get_rendering_engine(self, image_id, connection):
        if self.rendering_engine == 'openslide':
            return self._get_openslide_engine(image_id, connection)
        if self.rendering_engine == 'omero':
            return self._get_omero_engine(image_id, connection)
        else:
            raise UnknownRenderingEngine('%s is not a valid rendering engine' % self.rendering_engine)
