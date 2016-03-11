import requests
from argparse import ArgumentParser
from os import path, listdir
from hashlib import sha1
import sys
from urlparse import urljoin


class MiraxImporter(object):

    def __init__(self, source_folder, ome_base_url):
        self.source_folder = source_folder
        self.ome_url = urljoin(ome_base_url, 'mirax/register_file/')
        self.INDEX_FILE_MT = 'mirax/index'
        self.DATA_FOLDER_MT = 'mirax/datafolder'

    def _get_sha1(self, file_name):
        hasher = sha1()
        if path.isfile(file_name):
            with open(file_name) as f:
                hasher.update(f.read())
        elif path.isdir(file_name):
            for f in listdir(file_name):
                with open(path.join(file_name, f), 'rb') as fp:
                    for chunk in iter(lambda: fp.read(500*1024*1024), ''):
                        hasher.update(sha1(chunk).hexdigest())
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
        return label, details

    def _get_files_map(self):
        if path.exists(self.source_folder):
            files = listdir(self.source_folder)
            # exclude hidden files and folders
            files = [f for f in files if not f.startswith('.')]
            files_map = {}
            for f in files:
                print 'Getting details for file %s' % f
                label, details = self._get_file_details(path.join(self.source_folder, f))
                if label:
                    files_map.setdefault(label, []).append(details)
            return files_map
        else:
            raise ValueError('Path %s does not exist' % self.source_folder)

    def _save(self, file_details):
        response = requests.get(self.ome_url, params=file_details)
        if response.status_code == requests.codes.ok:
            print 'File saved, assigned ID: %s' % response.json()['omero_id']
            return True
        else:
            print 'Status code: ' % response.status_code
            return False

    def run(self):
        files_map = self._get_files_map()
        print 'SAVING DATA'
        for flabel, files in files_map.iteritems():
            if len(files) == 2 and flabel is not None:
                r0 = self._save(files[0])
                if r0:
                    self._save(files[1])


def get_parser():
    parser = ArgumentParser('Import MIRAX files and data folders to OMERO')
    parser.add_argument('--source-folder', type=str, required=True,
                        help='the folder containing MIRAX files and folders that will be imported')
    parser.add_argument('--ome-base-url', type=str, required=True,
                        help='the base URL of the OMERO.web server')
    return parser


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    importer = MiraxImporter(args.source_folder, args.ome_base_url)
    importer.run()

if __name__ == '__main__':
    main(sys.argv[1:])
