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

    Attributes:
        path (str): Path to the file.
        hash (str): Hash of the file.
    """
    def __new__(self, path, file_hash=None):
        return super(PathAndHash, self).__new__(self, path)

    def __init__(self, path, file_hash=None):
        self.path = path
        self.hash = file_hash

    def __repr__(self):
        return self.path
