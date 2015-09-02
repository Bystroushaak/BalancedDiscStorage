#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================


# Functions & classes =========================================================
class PathAndHash(str):
    """
    Path representation, which also holds hash.

    Note:
        This class is based on `str`, with which is fully interchangeable.

        ::

            str(PathAndHash(path="xe", hash="asd")) == "xe"

    Attributes:
        path (str): Path to the file.
        hash (str): Hash of the file.
    """
    def __new__(self, path, hash=None):
        return super(PathAndHash, self).__new__(self, path)

    def __init__(self, path, hash=None):
        super(PathAndHash, self).__init__(path)

        self.path = path
        self.hash = hash

    def __repr__(self):
        return self.path
