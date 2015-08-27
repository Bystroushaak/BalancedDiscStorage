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
    def __init__(self, path):
        self.path = path
        self._assert_path_is_rw()

        self._dir_limit = 32000
        self._read_bs = 2**16
        self._max_zipfiles = self._dir_limit
        self._hash_builder = hashlib.sha256

    def _assert_path_is_rw(self):
        if not os.path.exists(self.path):
            raise IOError("`%s` not found." % self.path)

        if not os.access(self.path, (os.R_OK or os.W_OK)):
            raise IOError(
                "Can't access `%s`, please check permissions." % self.path
            )

    def _get_file_iterator(self, file_obj):
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

    def _check_interface(self, file_obj):
        ERR = "`file_obj` have to be file-like object (.read() and .seek())!"
        assert hasattr(file_obj, "read"), ERR
        assert hasattr(file_obj, "seek"), ERR

    def _create_dir_path(self, file_hash, path=None, hash_list=None):
        # first, non-recursive call - parse `file_hash`
        if not hash_list:
            hash_list = list(file_hash)

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
            path=os.path.join(
                path,
                hash_list.pop(0)
            ),
            hash_list=hash_list
        )

    def dir_path_from_hash(self, file_hash, path=None, hash_list=None):
        # first, non-recursive call - parse `file_hash`
        if not hash_list:
            hash_list = list(file_hash)

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
        next_path = os.path.join(
            self.path,
            hash_list.pop(0)
        )
        if not os.path.exists(next_path):
            raise IOError("File not found in the structure.")

        # look into subdirectory
        return self.dir_path_from_hash(
            file_hash=file_hash,
            path=next_path,
            hash_list=hash_list
        )

    def file_path_from_hash(self, file_hash):
        return os.path.join(
            self.dir_path_from_hash(file_hash),
            file_hash
        )

    def add_file(self, file_obj):  # TODO: unpacker
        self._check_interface(file_obj)

        file_hash = self._get_hash(file_obj)
        dir_path = self._create_dir_path(file_hash)

        final_path = os.path.join(dir_path, file_hash)
        with open(final_path, "wb") as out_file:
            for part in self._get_file_iterator(file_obj):
                out_file.write(part)

        return final_path

    def unpack_zip(self, file_obj, path):
        old_cwd = os.getcwd()
        os.chdir(path)

        zip_obj = zipfile.ZipFile(file_obj)
        for cnt, zip_info in enumerate(zip_obj.infolist()):
            zip_obj.extract(zip_info)

            if cnt >= self._max_zipfiles:
                raise ValueError("Too many zipfiles (>%d)." % cnt)

        os.chdir(old_cwd)

    def add_archive_as_dir(self, zip_file_obj):
        self._check_interface(zip_file_obj)

        file_hash = self._get_hash(zip_file_obj)
        dir_path = self._create_dir_path(file_hash)
        full_path = os.path.join(dir_path, file_hash)

        if os.path.exists(full_path):
            shutil.rmtree(full_path)

        os.mkdir(full_path)
        self.unpack_zip(zip_file_obj, full_path)

        return full_path

    def delete_by_file(self, file_obj):
        self._check_interface(file_obj)

        file_hash = self._get_hash(file_obj)

        return self.delete_by_hash(file_hash)

    def delete_by_hash(self, file_hash):
        pass

    def delete_by_path(self, path):
        pass
