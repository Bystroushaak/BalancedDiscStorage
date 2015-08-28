#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import shutil
import os.path
import tempfile

import pytest

from BalancedDiscStorage import BalancedDiscStorage


# Variables ===================================================================
TEMP_DIR = ""


# Fixtures ====================================================================
# @pytest.fixture
# def fixture():
#     pass


# Tests =======================================================================
def setup_module():
    global TEMP_DIR

    TEMP_DIR = tempfile.mkdtemp()


def teardown_module():
    shutil.rmtree(TEMP_DIR)


def test_init():
    bds = BalancedDiscStorage(TEMP_DIR)

    with pytest.raises(TypeError):
        BalancedDiscStorage()


def test_rw_check():
    non_writeable = os.path.join(TEMP_DIR, "non_writeable")
    os.mkdir(non_writeable)
    os.chmod(non_writeable, 0000)

    with pytest.raises(IOError):
        BalancedDiscStorage(non_writeable)

    os.chmod(non_writeable, 0777)
    shutil.rmtree(non_writeable)
