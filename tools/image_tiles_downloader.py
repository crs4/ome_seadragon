#  Copyright (c) 2019, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from io import BytesIO
from PIL import Image
from requests import Session
import xml.etree.ElementTree as ET
import sys
import os
from urllib.parse import urljoin
import logging
from argparse import ArgumentParser
import math


class ImageTilesDownloader(object):

    def __init__(self, image_id, mirax_image, ome_base_url, output_folder=None,
                 log_level='INFO', log_file=None):
        self.logger = self.get_logger(log_level, log_file)
        self.image_id = image_id
        if mirax_image:
            self.get_dzi_url = urljoin(ome_base_url, 'mirax/deepzoom/get/%s.dzi' % self.image_id)
            self.get_tile_pattern = urljoin(
                ome_base_url, 'mirax/deepzoom/get/%s_files' % self.image_id
            )
            self.get_tile_pattern = urljoin(self.get_tile_pattern, '%s/%s_%s.%s')
            self.logger.info(self.get_tile_pattern)
        else:
            self.get_dzi_url = urljoin(ome_base_url, 'deepzoom/get/%s.dzi' % self.image_id)
            self.get_tile_pattern = urljoin(
                ome_base_url, 'deepzoom/get/%s_files/' % self.image_id
            )
            self.get_tile_pattern = urljoin(self.get_tile_pattern, '%s/%s_%s.%s')
            self.logger.info(self.get_tile_pattern)
        self.output_folder = output_folder
        if self.output_folder:
            try:
                os.makedirs(self.output_folder)
                self.logger.info('Output directory %s created' % self.output_folder)
            except OSError:
                self.logger.info('Using existing directory %s' % self.output_folder)
        self.session = Session()

    def get_logger(self, log_level='INFO', log_file=None, mode='a'):
        LOG_FORMAT = '%(asctime)s|%(levelname)-8s|%(message)s'
        LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'

        logger = logging.getLogger('tiler_downloader')
        if not isinstance(log_level, int):
            try:
                log_level = getattr(logging, log_level)
            except AttributeError:
                raise ValueError('Unsupported literal log level: %s' % log_level)
        logger.setLevel(log_level)
        logger.handlers = []
        if log_file:
            handler = logging.FileHandler(log_file, mode=mode)
        else:
            handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _get_image_infos(self):
        response = self.session.get(self.get_dzi_url)
        if response.status_code == 200:
            dzi = ET.fromstring(response.text)
            self.logger.debug(response.text)
            return {
                'format': dzi.get('Format'),
                'tile_size': int(dzi.get('TileSize')),
                'width': int(dzi.getchildren()[0].get('Width')),
                'height': int(dzi.getchildren()[0].get('Height'))
            }
        else:
            self.logger.error(response)

    def _get_max_zoom_level(self, img_height, img_width):
        return int(math.ceil(math.log(max(img_height, img_width), 2)))

    def _get_scale_factor(self, level, max_level):
        return math.pow(0.5, max_level - level)

    def _get_scaled_dimension(self, img_width, img_height, level, max_level):
        scale_factor = self._get_scale_factor(level, max_level)
        return {
            'width': int(math.ceil(img_width * scale_factor)),
            'height': int(math.ceil(img_height * scale_factor))
        }

    def _save_tile(self, image_data, output_folder, file_name):
        with open(os.path.join(output_folder, file_name), 'w') as ofile:
            img = Image.open(BytesIO(image_data))
            img.save(ofile)

    def _get_tiles(self, level, scaled_width, scaled_height, tile_size, tile_format):
        if self.output_folder:
            tiles_output_folder = os.path.join(self.output_folder, 'level_%d' % level)
            try:
                os.makedirs(tiles_output_folder)
            except OSError:
                pass
        for x in range(scaled_width / tile_size):
            for y in range(scaled_height / tile_size):
                tr = self.session.get(self.get_tile_pattern % (level, x, y, tile_format))
                if self.output_folder:
                    self._save_tile(tr.content, tiles_output_folder, '%d_%d.%s' % (x, y, tile_format))

    def run(self):
        image_infos = self._get_image_infos()
        max_level = self._get_max_zoom_level(image_infos['height'], image_infos['width'])
        self.logger.info('MAX LEVEL: %d' % max_level)
        for x in range(max_level + 1):
            self.logger.info('### Level %d ###' % x)
            scaled_dimensions = self._get_scaled_dimension(image_infos['width'], image_infos['height'],
                                                           x, max_level)
            self.logger.info('Scales dimensions %r' % scaled_dimensions)
            self._get_tiles(x, scaled_dimensions['width'], scaled_dimensions['height'],
                            image_infos['tile_size'], image_infos['format'])



def get_parser():
    parser = ArgumentParser('Download tiles for a given image and optionally save them on file system')
    parser.add_argument('--image-id', type=str, required=True,
                        help='The ID of the image that will be downloaded')
    parser.add_argument('--mirax', action='store_true',
                        help='Add this flag to fetch a MIRAX file')
    parser.add_argument('--ome-base-url', type=str, required=True,
                        help='the base URL of the OMERO.web server')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='output folder where the tiles will be saved')
    parser.add_argument('--log-level', type=str, default='INFO',
                        help='log level (default=INFO)')
    parser.add_argument('--log-file', type=str, default=None,
                        help='log file (default=stderr)')
    return parser


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    downloader = ImageTilesDownloader(args.image_id, args.mirax, args.ome_base_url,
                                      args.output_dir, args.log_level, args.log_file)
    downloader.run()

if __name__ == '__main__':
    main(sys.argv[1:])