#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import hashlib


# Functions & classes =========================================================
class BalancedDiscStorage(object):
    def __init__(self, path):
        self.path = path
        self._assert_path_is_rw()

        self._dir_limit = 32000
        self._read_bs = 2**16
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

    def _get_file_path(self, file_hash, create_path=False):
        hash_list = list(file_hash)
        path = os.path.join(self.path, hash_list.pop(0))

        if os.path.exists(path):
            files = os.listdir(path)
        else:
            pass

    def add_file(self, file_obj, unpacker=None):  # TODO: unpacker
        self._check_interface(file_obj)

        file_hash = self._get_hash(file_obj)

    def delete_by_file(self, file_obj):
        file_hash = _get_hash(file_obj)

        return self.delete_by_hash(file_hash)

    def delete_by_hash(self, file_hash):
        pass

    def delete_by_path(self, path):
        pass
