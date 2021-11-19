#  Copyright (c) 2021, CRS4
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

from requests.models import Response


class ServerError(Exception):
    pass


class MiraxImporter(object):

    def __init__(self, mirax_file, ome_base_url, chunk_size, log_level='INFO', log_file=None):
        self.mirax_file = mirax_file
        self.ome_save_url = urljoin(ome_base_url, 'file/register/')
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
                raise ValueError(
                    'Unsupported literal log level: %s' % log_level)
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

    def _check_mirax_dataset(self, mirax_file_path):
        if path.isfile(mirax_file_path):
            if path.isdir(path.splitext(mirax_file_path)[0]):
                return path.splitext(mirax_file_path)[0]
            else:
                raise ValueError(
                    'Cannot find MIRAX data folder for file %s', mirax_file_path)
        else:
            raise ValueError('%s is not a valid file', mirax_file_path)

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

    def _save(self, file_details):
        self.logger.debug('Saving data for file %s', file_details['name'])
        response = requests.get(self.ome_save_url, params=file_details)
        if response.status_code == requests.codes.ok:
            self.logger.debug('File saved, assigned ID: %s',
                              response.json()['omero_id'])
            return True, response.json()['omero_id']
        else:
            self.logger.debug('Status code: %d', response.status_code)
            return False, response.status_code

    def _clear(self, base_label):
        response = requests.get(urljoin(self.ome_delete_url, base_label))
        return response.status_code

    def run(self):
        self.logger.info('Importing file %s', self.mirax_file)
        mirax_data_folder = self._check_mirax_dataset(self.mirax_file)
        mirax_file_label, mirax_file_details = self._get_file_details(self.mirax_file)
        mirax_df_label, mirax_df_details = self._get_file_details(mirax_data_folder)
        r0_status, r0_response = self._save(mirax_file_details)
        if r0_status:
            r1_status, r1_response = self._save(mirax_df_details)
            if not r1_status:
                self.logger.warning(
                    'Error while saving MIRAX data folder, removing MIRAX file from database')
                d0_status = self._clear(mirax_file_label)
                if d0_status != requests.codes.ok:
                    raise ServerError('MIRAX file %s not cleaned properly' % mirax_file_label)
        else:
            raise ServerError(
                'Unable to save MIRAX file, server returned error code %s', r0_response)
        self.logger.info('Job completed')

def get_parser():
    parser = ArgumentParser('Import a dingle MIRAX file and related data folder to OMERO')
    parser.add_argument('--mirax-file', type=str, required=True,
                        help='the path to MIRAX file to be imported, MIRAX data folder with the same name must be in the same path')
    parser.add_argument('--ome-base-url', type=str, required=True,
                        help='the base URL of the OMERO.web server')
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
    importer = MiraxImporter(args.mirax_file, args.ome_base_url, args.chunk_size,
                             args.log_level, args.log_file)
    importer.run()

if __name__ == '__main__':
    main(sys.argv[1:])
