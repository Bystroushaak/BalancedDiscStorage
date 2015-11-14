#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import shutil
import hashlib

from path_and_hash import PathAndHash


# Functions & classes =========================================================
class BalancedDiscStorage(object):
    """
    Store files, make sure, that there are never more files in one directory
    than :attr:`_dir_limit`.
    """
    def __init__(self, path, dir_limit=32000):
        self.path = path  #: Path on which the storage operates.
        self._assert_path_is_rw()

        self.dir_limit = dir_limit  #: Maximal number of files in directory.
        self.read_bs = 2**16  #: File read blocksize.
        self.hash_builder = hashlib.sha256  #: Hashing function used for FN.

    def _assert_path_is_rw(self):
        """
        Make sure, that `self.path` exists, is directory a readable/writeable.

        Raises:
            IOError: In case that any of the assumptions failed.
            ValueError: In case that `self.path` is not set.
        """
        if not self.path:
            raise ValueError("`path` argument must be set!")

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
        `self.read_bs` chunks.

        Args:
            file_obj (file): File-like object.

        Return:
            iterator: Iterator reading the file-like object in chunks.
        """
        file_obj.seek(0)

        return iter(lambda: file_obj.read(self.read_bs), '')

    def _get_hash(self, file_obj):
        """
        Compute hash for the `file_obj`.

        Attr:
            file_obj (obj): File-like object with ``.write()`` and ``.seek()``.

        Returns:
            str: Hexdigest of the hash.
        """
        size = 0
        hash_buider = self.hash_builder()
        for piece in self._get_file_iterator(file_obj):
            hash_buider.update(piece)
            size += len(piece)

        file_obj.seek(0)

        return "%s_%x" % (hash_buider.hexdigest(), size)

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
        if len(files) < self.dir_limit:
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
            str: Path for given `file_hash` contained in :class:`.PathAndHash`\
                 object.

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
                return PathAndHash(path=full_path, hash=file_hash)

            return PathAndHash(path=full_path + "/", hash=file_hash)

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
            obj: Path where the file-like object is stored contained with hash\
                 in :class:`.PathAndHash` object.

        Raises:
            AssertionError: If the `file_obj` is not file-like object.
            IOError: If the file couldn't be added to storage.
        """
        BalancedDiscStorage._check_interface(file_obj)

        file_hash = self._get_hash(file_obj)
        dir_path = self._create_dir_path(file_hash)

        final_path = os.path.join(dir_path, file_hash)

        def copy_to_file(from_file, to_path):
            with open(to_path, "wb") as out_file:
                for part in self._get_file_iterator(from_file):
                    out_file.write(part)

        try:
            copy_to_file(from_file=file_obj, to_path=final_path)
        except Exception:
            os.unlink(final_path)
            raise

        return PathAndHash(path=final_path, hash=file_hash)

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

    def __repr__(self):
        return "%s(path=%s, dir_limit=%d)" % (
            self.__class__.__name__,
            repr(self.path),
            self.dir_limit
        )
