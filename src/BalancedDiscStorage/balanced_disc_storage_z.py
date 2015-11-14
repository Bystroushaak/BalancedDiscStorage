#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import shutil
import zipfile

from path_and_hash import PathAndHash
from balanced_disc_storage import BalancedDiscStorage


# Functions & classes =========================================================
class BalancedDiscStorageZ(BalancedDiscStorage):
    """
    This class is the same as :class:`.BalancedDiscStorage`, but it also allows
    adding the ``.zip`` files, which are unpacked to proper path in storage.
    """
    def __init__(self, path):
        super(BalancedDiscStorageZ, self).__init__(path)

        self.max_zipfiles = self.dir_limit  #: How many files may be in .zip

    def _unpack_zip(self, file_obj, path):
        """
        Unpack .zip archive in `file_obj` to given `path`. Make sure, that it
        fits into limits (see :attr:`._max_zipfiles` for details).

        Args:
            file_obj (file): Opened file-like object.
            path (str): Path into which the .zip will be unpacked.

        Raises:
            ValueError: If there is too many files in .zip archive.
        """
        old_cwd = os.getcwd()
        os.chdir(path)

        zip_obj = zipfile.ZipFile(file_obj)
        for cnt, zip_info in enumerate(zip_obj.infolist()):
            zip_obj.extract(zip_info)

            if cnt + 1 > self.max_zipfiles:
                os.chdir(old_cwd)

                msg = "Too many files in .zip "
                msg += "(self.max_zipfiles == {}, but {} given).".format(
                    self.max_zipfiles,
                    cnt + 1,
                )
                raise ValueError(msg)

        os.chdir(old_cwd)

    def add_archive_as_dir(self, zip_file_obj):
        """
        Add archive to the storage and unpack it.

        Args:
            zip_file_obj (file): Opened file-like object.

        Returns:
            obj: Path where the `zip_file_obj` was unpacked wrapped in \
                 :class:`.PathAndHash` structure.

        Raises:
            ValueError: If there is too many files in .zip archive. \
                        See :attr:`._max_zipfiles` for details.
            AssertionError: If the `zip_file_obj` is not file-like object.
        """
        BalancedDiscStorage._check_interface(zip_file_obj)

        file_hash = self._get_hash(zip_file_obj)
        dir_path = self._create_dir_path(file_hash)
        full_path = os.path.join(dir_path, file_hash)

        if os.path.exists(full_path):
            shutil.rmtree(full_path)

        os.mkdir(full_path)

        try:
            self._unpack_zip(zip_file_obj, full_path)
        except Exception:
            shutil.rmtree(full_path)
            raise

        return PathAndHash(path=full_path, hash=file_hash)
