#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from BalancedDiscStorage.path_and_hash import PathAndHash


# Tests =======================================================================
def test_path_and_hash():
    assert PathAndHash("hello") == "hello"
    assert PathAndHash("hello").hash == None


def test_hash_constructor():
    ph = PathAndHash("/somepath", "hfffhsomehash")

    assert ph.path == "/somepath"
    assert ph.hash == "hfffhsomehash"

    assert str(ph) == "/somepath"
