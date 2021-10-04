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

from .. import settings

from uuid import uuid4
import os, zipfile, tarfile, tiledb, zarr
import logging

from .utils import switch_to_default_search_group

logger = logging.getLogger(__name__)


class InvalidDatasetPath(Exception):
    pass


class ArchiveFormatError(Exception):
    pass


class DatasetFormatError(Exception):
    pass


class DatasetPathAlreadyExistError(Exception):
    pass


def get_dataset_file_path(dataset_file_name):
    if settings.DATASETS_REPOSITORY is not None:
        dataset_path = os.path.join(settings.DATASETS_REPOSITORY, dataset_file_name)
        if os.path.isdir(dataset_path) or os.path.isfile(dataset_path):
            return dataset_path, os.path.isdir(dataset_path)
        else:
            raise InvalidDatasetPath('Path {0} not found'.format(dataset_path))
    else:
        raise settings.ServerConfigError('DATASETS default folder was not configured properly')


def _check_tiledb_dataset(dataset_path):
    logger.info('Checking dataset {0} for TILEDB compatibility'.format(dataset_path))
    try:
        x = tiledb.open(dataset_path)
        x.close()
        return 'dataset-folder/tiledb'
    except tiledb.TileDBError:
        return None


def _check_zarr_dataset(dataset_path):
    logger.info('Checking dataset {0} for ZARR compatibility'.format(dataset_path))
    x = zarr.open(dataset_path, 'r')
    if len(list(x.arrays())) > 0:
        if os.path.isdir(dataset_path):
            return 'dataset-folder/zarr'
        else:
            return 'dataset-archive/zarr'
    else:
        return None


def check_dataset(dataset_path, archive_dir):
    mtype = _check_zarr_dataset(dataset_path)
    if mtype is None:
        if archive_dir:
            mtype = _check_tiledb_dataset(dataset_path)
            if mtype is None:
                raise DatasetFormatError('Dataset {0} is not a valid TileDB or ZARR archive'.format(dataset_path))
        else:
            if zipfile.is_zipfile(dataset_path):
                mtype = 'application/zip'
            elif tarfile.is_tarfile(dataset_path):
                mtype = 'application/x-tar'
            else:
                raise DatasetFormatError('Dataset {0} is not a valid ZARR, ZIP or TAR archive'.format(dataset_path))
    return mtype


def extract(archive_handler, out_folder):
    dataset_label = str(uuid4())
    out_folder = dest_folder = os.path.join(out_folder, dataset_label)
    if not os.path.isdir(dest_folder):
        logger.info('Extracting archive to folder {0}'.format(out_folder))
        archive_handler.extractall(out_folder)
        logger.info('Dataset label: {0} -- Destination folder: {1}'.format(dataset_label, dest_folder))
        return dataset_label, dest_folder
    else:
        raise DatasetPathAlreadyExistError('Destination path {0} for archive extraction already exists'.format(dest_folder))


def extract_zip_archive(archive_file, out_folder):
    with zipfile.ZipFile(archive_file, 'r') as f:
        return extract(f, out_folder)


def extract_tar_archive(archive_file, out_folder):
    with tarfile.TarFile(archive_file, 'r') as f:
        return extract(f, out_folder)


def rename_archive(archive_file, out_folder=settings.DATASETS_REPOSITORY):
    _, ext = os.path.splitext(archive_file)
    new_dset_label = str(uuid4())
    new_fpath = os.path.join(out_folder, "{0}{1}".format(new_dset_label, ext))
    os.rename(archive_file, new_fpath)
    return new_dset_label, new_fpath


def extract_archive(archive_file, out_folder=settings.DATASETS_REPOSITORY, keep_archive=False):
    if zipfile.is_zipfile(archive_file):
        ds_label, dest_folder = extract_zip_archive(archive_file, out_folder)
    elif tarfile.is_tarfile(archive_file):
        ds_label, dest_folder = extract_tar_archive(archive_file, out_folder)
    else:
        raise ArchiveFormatError('Archive file {0} is nor ZIP or TAR format'.format(archive_file))
    logger.info('Archive extraction completed')
    if not keep_archive:
        logger.info('Deleting archive file')
        os.remove(archive_file)
    return ds_label, dest_folder


def _dataset_to_json(dataset_obj):
    return {
        'id': dataset_obj.getId(),
        'label': dataset_obj.getName(),
        'mimetype': dataset_obj.getMimetype()
    }

def get_datasets(connection):
    switch_to_default_search_group(connection)
    mtypes_filter = ['dataset-folder/tiledb', 'dataset-folder/zarr', 'dataset-archive/zarr']
    datasets = list()
    for mf in mtypes_filter:
        query_filter = {'mimetype': mf}
        datasets.extend(connection.getObjects('OriginalFile', attributes=query_filter))
    return [_dataset_to_json(d) for d in datasets]
