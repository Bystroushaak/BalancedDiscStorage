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

from os.path import join

import pytest

from BalancedDiscStorage import BalancedDiscStorage


# Variables ===================================================================
TEMP_DIR = ""


# Functions ===================================================================
def data_dir_context(filename):
    return join(
        os.path.dirname(__file__),
        "files",
        filename
    )


def data_file_context(filename):
    return open(
        data_dir_context(filename)
    )


# Fixtures ====================================================================
@pytest.fixture
def bds():
    return BalancedDiscStorage(TEMP_DIR)


@pytest.fixture
def a_file():
    return data_file_context("a_file")


@pytest.fixture
def aa_file():
    return data_file_context("aa_file")


@pytest.fixture
def b_file():
    return data_file_context("b_file")


@pytest.fixture
def a_file_hash():
    return "aea92132c4cbeb263e6ac2bf6c183b5d81737f179f21efdc5863739672f0f470"


@pytest.fixture
def b_file_hash():
    return "b17ef6d19c7a5b1ee83b907c595526dcb1eb06db8227d650d5dda0a9f4ce8cd9"


@pytest.fixture
def aa_file_hash():
    return "aae02129362d611717b6c00ad8d73bf820a0f6d88fca8e515cafe78d3a335965"


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


def test_init_exists():
    with pytest.raises(IOError):
        BalancedDiscStorage("/azgabash")


def test_init_is_directory():
    fn_path = join(TEMP_DIR, "azgabash")
    with open(fn_path, "w") as f:
        f.write("-")

    with pytest.raises(IOError):
        BalancedDiscStorage(fn_path)

    os.unlink(fn_path)


def test_rw_check():
    non_writeable = join(TEMP_DIR, "non_writeable")
    os.mkdir(non_writeable)
    os.chmod(non_writeable, 0000)

    with pytest.raises(IOError):
        BalancedDiscStorage(non_writeable)

    os.chmod(non_writeable, 0777)
    shutil.rmtree(non_writeable)
