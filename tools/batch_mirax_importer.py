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

import requests
from argparse import ArgumentParser
from os import path, listdir
from hashlib import sha1
import sys
from urllib.parse import urljoin
import logging


class MiraxBatchImporter(object):

    def __init__(self, source_folder, ome_base_url, chunk_size, log_level='INFO', log_file=None):
        self.source_folder = source_folder
        self.ome_slides_list_url = urljoin(ome_base_url, 'get/images/index/')
        self.ome_save_url = urljoin(ome_base_url, 'mirax/register_file/')
        self.ome_delete_url = urljoin(ome_base_url, 'mirax/delete_files/')
        self.INDEX_FILE_MT = 'mirax/index'
        self.DATA_FOLDER_MT = 'mirax/datafolder'
        self.big_files_chunk_size = chunk_size * 1024 * 1024
        self.logger = self.get_logger(log_level, log_file)

    def get_logger(self, log_level='INFO', log_file=None, mode='a'):
        LOG_FORMAT = '%(asctime)s|%(levelname)-8s|%(message)s'
        LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'

        logger = logging.getLogger('mirax_importer')
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

    def _get_sha1(self, file_name):
        hasher = sha1()
        if path.isfile(file_name):
            with open(file_name, 'rb') as f:
                hasher.update(f.read())
        elif path.isdir(file_name):
            for f in listdir(file_name):
                with open(path.join(file_name, f), 'rb') as fp:
                    for chunk in iter(lambda: fp.read(self.big_files_chunk_size), b''):
                        hasher.update(chunk)
        return hasher.hexdigest()

    def _get_file_details(self, file_name):
        label = None
        details = {
            'path': path.realpath(file_name),
            'sha1': self._get_sha1(file_name)
        }
        if path.isfile(file_name):
            label, ext = path.splitext(path.basename(file_name))
            if ext.lower() == '.mrxs':
                details.update({
                    'name': label,
                    'mimetype': self.INDEX_FILE_MT,
                    'size': path.getsize(file_name)
                })
            else:
                label, details = None, None
        elif path.isdir(file_name):
            label = path.basename(file_name)
            details.update({
                'name': label,
                'mimetype': self.DATA_FOLDER_MT,
                'size': sum([path.getsize(path.join(file_name, f))
                             for f in listdir(file_name)]),
                })
        self.logger.debug('Details for file %s: %r', file_name, details)
        return label, details

    def _clean_existing_slides(self, files_list):
        response = requests.get(self.ome_slides_list_url)
        slides_list = [x['name'] for x in response.json()]
        cleaned_list = []
        for f in files_list:
            if not f.split('.')[0] in slides_list:
                cleaned_list.append(f)
        return cleaned_list

    def _get_files_map(self):
        if path.exists(self.source_folder):
            files = listdir(self.source_folder)
            # exclude hidden files and folders
            files = [f for f in files if not f.startswith('.')]
            cleaned_files = self._clean_existing_slides(files)
            if len(cleaned_files) == 0:
                self.logger.info('Nothing to import, exit')
                sys.exit(0)
            files_map = {}
            self.logger.info('Found %d files, building files map', len(cleaned_files))
            for f in cleaned_files:
                self.logger.debug('Getting details for file %s', f)
                label, details = self._get_file_details(path.join(self.source_folder, f))
                if label:
                    files_map.setdefault(label, []).append(details)
            return files_map
        else:
            raise ValueError('Path %s does not exist' % self.source_folder)

    def _save(self, file_details):
        self.logger.debug('Saving data for file %s', file_details['name'])
        response = requests.get(self.ome_save_url, params=file_details)
        if response.status_code == requests.codes.ok:
            self.logger.debug('File saved, assigned ID: %s', response.json()['omero_id'])
            return True
        else:
            self.logger.debug('Status code: %d', response.status_code)
            return False

    def _clear(self, labels_list):
        for l in labels_list:
            self.logger.debug('Deleting files for label %s', l)
            response = requests.get(urljoin(self.ome_delete_url, l))
            self.logger.debug('Deleted %d elements (deletion successful: %s)',
                              response.json()['deleted_count'], response.json()['success'])

    def run(self, clear_existing=False):
        self.logger.info('Starting import job')
        self.logger.info('Collecting data')
        files_map = self._get_files_map()
        if clear_existing:
            self.logger.info('Cleaning existing data')
            self._clear(files_map.keys())
            self.logger.info('Cleanup completed')
        self.logger.info('Saving data')
        for flabel, files in files_map.items():
            if len(files) == 2 and flabel is not None:
                r0 = self._save(files[0])
                if r0:
                    self._save(files[1])
        self.logger.info('Import job completed')


def get_parser():
    parser = ArgumentParser('Import MIRAX files and data folders to OMERO')
    parser.add_argument('--source-folder', type=str, required=True,
                        help='the folder containing MIRAX files and folders that will be imported')
    parser.add_argument('--ome-base-url', type=str, required=True,
                        help='the base URL of the OMERO.web server')
    parser.add_argument('--clear', action='store_true',
                        help='clear existing files with same name before saving')
    parser.add_argument('--chunk-size', type=int, default=50,
                        help='size in MB of chunks that will be read to calculate the SHA1 for big files (default 50MB)')
    parser.add_argument('--log-level', type=str, default='INFO',
                        help='log level (default=INFO)')
    parser.add_argument('--log-file', type=str, default=None,
                        help='log file (default=stderr)')
    return parser


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    importer = MiraxBatchImporter(args.source_folder, args.ome_base_url, args.chunk_size,
                                  args.log_level, args.log_file)
    importer.run(args.clear)

if __name__ == '__main__':
    main(sys.argv[1:])
