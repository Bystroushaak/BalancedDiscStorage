#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import shutil
import hashlib
import zipfile


# Functions & classes =========================================================
class BalancedDiscStorage(object):
    """
    Store files, make sure, that there are never more files in one directory
    than :attr:`_dir_limit`.
    """
    def __init__(self, path):
        self.path = path  #: Path on which the storage operates.
        self._assert_path_is_rw()

        self._dir_limit = 32000  #: Maximum number of files in directory.
        self._read_bs = 2**16  #: File read blocksize.
        self._max_zipfiles = self._dir_limit  #: How many files may be in .zip
        self._hash_builder = hashlib.sha256  #: Hashing function used for FN.

    def _assert_path_is_rw(self):
        """
        Make sure, that `self.path` exists, is directory a readable/writeable.

        Raises:
            IOError: In case that any of the assumptions failed.
        """
        if not os.path.exists(self.path):
            raise IOError("`%s` not found." % self.path)

        if not os.path.isdir(self.path):
            raise IOError("`%s` is not a directory!" % self.path)

        if not os.access(self.path, (os.R_OK or os.W_OK)):
            raise IOError(
                "Can't access `%s`, please check permissions." % self.path
            )

    def _get_file_iterator(self, file_obj):
        """
        For given `file_obj` return iterator, which will read the file in
        `self._read_bs` chunks.

        Args:
            file_obj (file): File-like object.

        Return:
            iterator: Iterator reading the file-like object in chunks.
        """
        file_obj.seek(0)

        return iter(lambda: file_obj.read(self._read_bs), '')

    def _get_hash(self, file_obj):
        """
        Compute hash for the `file_obj`.

        Attr:
            file_obj (obj): File-like object with ``.write()`` and ``.seek()``.

        Returns:
            str: Hexdigest of the hash.
        """
        hash_buider = self._hash_builder()
        for piece in self._get_file_iterator(file_obj):
            hash_buider.update(piece)

        file_obj.seek(0)

        return hash_buider.hexdigest()

    @staticmethod
    def _check_interface(file_obj):
        """
        Make sure, that `file_obj` has `.read()` and `.seek()` attributes.

        Args:
            file_obj (file): File like object.

        Raises:
            AssertionError: In case that assumptions fails.
        """
        ERR = "`file_obj` have to be file-like object (.read() and .seek())!"
        assert hasattr(file_obj, "read"), ERR
        assert hasattr(file_obj, "seek"), ERR

    def _create_dir_path(self, file_hash, path=None, hash_list=None):
        """
        Create proper filesystem paths for given `file_hash`.

        Args:
            file_hash (str): Hash of the file for which the path should be
                      created.
            path (str, default None): Recursion argument, don't set this.
            hash_list (list, default None): Recursion argument, don't set this.

        Returns:
            str: Created path.
        """
        # first, non-recursive call - parse `file_hash`
        if hash_list is None:
            hash_list = list(file_hash)

        if not hash_list:
            raise IOError("Directory structure is too full!")

        # first, non-recursive call - look for subpath of `self.path`
        if not path:
            path = os.path.join(
                self.path,
                hash_list.pop(0)
            )

        # if the path not yet exists, create it and work on it
        if not os.path.exists(path):
            os.mkdir(path)
            return self._create_dir_path(
                file_hash=file_hash,
                path=path,
                hash_list=hash_list
            )

        files = os.listdir(path)

        # file is already in storage
        if file_hash in files:
            return path

        # if the directory is not yet full, use it
        if len(files) < self._dir_limit:
            return path

        # in full directories create new sub-directories
        return self._create_dir_path(
            file_hash=file_hash,
            path=os.path.join(path, hash_list.pop(0)),
            hash_list=hash_list
        )

    def file_path_from_hash(self, file_hash, path=None, hash_list=None):
        """
        For given `file_hash`, return path on filesystem.

        Args:
            file_hash (str): Hash of the file, for which you wish to know the
                      path.
            path (str, default None): Recursion argument, don't set this.
            hash_list (list, default None): Recursion argument, don't set this.

        Returns:
            str: Path for given `file_hash`.

        Raises:
            IOError: If the file with corresponding `file_hash` is not in \
                     storage.
        """
        # first, non-recursive call - parse `file_hash`
        if hash_list is None:
            hash_list = list(file_hash)

        if not hash_list:
            raise IOError("Directory structure is too full!")

        # first, non-recursive call - look for subpath of `self.path`
        if not path:
            path = os.path.join(
                self.path,
                hash_list.pop(0)
            )

        files = os.listdir(path)

        # is the file/unpacked archive in this `path`?
        if file_hash in files:
            full_path = os.path.join(path, file_hash)

            if os.path.isfile(full_path):
                return full_path

            return full_path + "/"

        # end of recursion, if there are no more directories to look into
        next_path = os.path.join(path, hash_list.pop(0))
        if not os.path.exists(next_path):
            raise IOError("File not found in the structure.")

        # look into subdirectory
        return self.file_path_from_hash(
            file_hash=file_hash,
            path=next_path,
            hash_list=hash_list
        )

    def add_file(self, file_obj):
        """
        Add new file into the storage.

        Args:
            file_obj (file): Opened file-like object.

        Returns:
            str: Path where the file-like object is stored.

        Raises:
            AssertionError: If the `file_obj` is not file-like object.
            IOError: If the file couldn't be added to storage.
        """
        BalancedDiscStorage._check_interface(file_obj)

        file_hash = self._get_hash(file_obj)
        dir_path = self._create_dir_path(file_hash)

        final_path = os.path.join(dir_path, file_hash)
        with open(final_path, "wb") as out_file:
            for part in self._get_file_iterator(file_obj):
                out_file.write(part)

        return final_path

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

            if cnt >= self._max_zipfiles:
                raise ValueError("Too many zipfiles (>%d)." % cnt)

        os.chdir(old_cwd)

    def add_archive_as_dir(self, zip_file_obj):
        """
        Add archive to the storage and unpack it.

        Args:
            zip_file_obj (file): Opened file-like object.

        Returns:
            str: Path where the `zip_file_obj` was unpacked.

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
        self._unpack_zip(zip_file_obj, full_path)

        return full_path

    def delete_by_file(self, file_obj):
        """
        Remove file from the storage. File is identified by opened `file_obj`,
        from which the hashes / path are computed.

        Args:
            file_obj (file): Opened file-like object, which is used to compute
                     hashes.

        Raises:
            IOError: If the `file_obj` is not in storage.
        """
        BalancedDiscStorage._check_interface(file_obj)

        file_hash = self._get_hash(file_obj)

        return self.delete_by_hash(file_hash)

    def delete_by_hash(self, file_hash):
        """
        Remove file/archive by it's `file_hash`.

        Args:
            file_hash (str): Hash, which is used to find the file in storage.

        Raises:
            IOError: If the file for given `file_hash` was not found in \
                     storage.
        """
        full_path = self.file_path_from_hash(file_hash)

        return self.delete_by_path(full_path)

    def _recursive_remove_blank_dirs(self, path):
        """
        Make sure, that blank directories are removed from the storage.

        Args:
            path (str): Path which you suspect that is blank.
        """
        path = os.path.abspath(path)

        # never delete root of the storage or smaller paths
        if path == self.path or len(path) <= len(self.path):
            return

        # if the path doesn't exists, go one level upper
        if not os.path.exists(path):
            return self._recursive_remove_blank_dirs(
                os.path.dirname(path)
            )

        # if the directory contains files, end yourself
        if os.listdir(path):
            return

        # blank directories can be removed
        shutil.rmtree(path)

        # go one level up, check whether the directory is blank too
        return self._recursive_remove_blank_dirs(
            os.path.dirname(path)
        )

    def delete_by_path(self, path):
        """
        Delete file/directory identified by `path` argument.

        Warning:
            `path` have to be in :attr:`path`.

        Args:
            path (str): Path of the file / directory you want to remove.

        Raises:
            IOError: If the file / directory doesn't exists, or is not in \
                     :attr:`path`.
        """
        if not os.path.exists(path):
            raise IOError("Unknown path '%s'!" % path)

        if not path.startswith(self.path):
            raise IOError(
                "Path '%s' is not in the root of the storage ('%s')!" % (
                    path,
                    self.path
                )
            )

        if os.path.isfile(path):
            os.unlink(path)
            return self._recursive_remove_blank_dirs(path)

        shutil.rmtree(path)
        self._recursive_remove_blank_dirs(path)
