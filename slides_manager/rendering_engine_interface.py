from abc import ABCMeta, abstractmethod
import os
import logging

from ome_seadragon import settings


class RenderingEngineInterface(object):

    __metaclass__ = ABCMeta

    def __init__(self, image_id, connection):
        self.connection = connection
        self.image_id = image_id
        self.logger = logging.getLogger(__name__)

    def _get_image_object(self):
        return self.connection.getObject('Image', self.image_id)

    def _get_image_path(self, original_file_source=False, file_mimetype=None):
        if img is None:
            return None
        else:
            return os.path.join(
                settings.IMGS_REPOSITORY,
                settings.IMGS_FOLDER,
                img.getImportedImageFilePaths()['server_paths'][0]
            )

    @abstractmethod
    def get_openseadragon_config(self, original_file_source=False, file_mimetype=None):
        pass

    @abstractmethod
    def get_dzi_description(self, original_file_source=False, file_mimetype=None):
        pass

    @abstractmethod
    def get_thumbnail(self, size, original_file_source=False, file_mimeype=None):
        pass

    @abstractmethod
    def get_tile(self, level, column, row, original_file_source=False, file_mimetype=None):
        pass
