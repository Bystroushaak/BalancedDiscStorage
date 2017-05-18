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
TEMP_DIR = None


# Functions ===================================================================
def data_dir_context(filename):
    return join(
        os.path.dirname(__file__),
        "files",
        filename
    )


def data_file_context(filename):
    return open(data_dir_context(filename), "rb")


# Fixtures ====================================================================
@pytest.fixture
def bds():
    return BalancedDiscStorage(TEMP_DIR)


@pytest.fixture
def a_file():
    return data_file_context("a_file")


@pytest.fixture
def b_file():
    return data_file_context("b_file")


@pytest.fixture
def aa_file():
    return data_file_context("aa_file")


@pytest.fixture
def a_file_hash():
    return "aea92132c4cbeb263e6ac2bf6c183b5d81737f179f21efdc5863739672f0f470_2"


@pytest.fixture
def b_file_hash():
    return "b17ef6d19c7a5b1ee83b907c595526dcb1eb06db8227d650d5dda0a9f4ce8cd9_2"


@pytest.fixture
def aa_file_hash():
    return "aae02129362d611717b6c00ad8d73bf820a0f6d88fca8e515cafe78d3a335965_3"


@pytest.fixture
def b_file_path():
    return join(TEMP_DIR, "b", b_file_hash())


@pytest.fixture
def aa_file_path():
    file_hash = aa_file_hash()

    return join(TEMP_DIR, file_hash[0], file_hash[1], aa_file_hash())


# Setup =======================================================================
def setup_module():
    global TEMP_DIR

    TEMP_DIR = tempfile.mkdtemp()


def teardown_module():
    shutil.rmtree(TEMP_DIR)


# Tests =======================================================================
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
    os.chmod(non_writeable, 0o000)

    with pytest.raises(IOError):
        BalancedDiscStorage(non_writeable)

    os.chmod(non_writeable, 0o777)
    shutil.rmtree(non_writeable)


def test_add_file(bds, a_file, a_file_hash):
    bds.add_file(a_file)

    first_branch = join(TEMP_DIR, "a")
    first_added_file = join(first_branch, a_file_hash)

    assert os.path.exists(first_branch)
    assert os.path.isdir(first_branch)
    assert os.path.exists(first_added_file)
    assert os.path.isfile(first_added_file)


def test_add_multiple_files(bds, b_file, aa_file, aa_file_hash, b_file_path):
    bds.dir_limit = 1

    bds.add_file(b_file)
    bds.add_file(aa_file)

    first_branch = join(TEMP_DIR, "a")
    deep_branch = join(first_branch, "a")
    third_added_file = join(deep_branch, aa_file_hash)

    assert os.path.exists(first_branch)
    assert os.path.isdir(first_branch)
    assert os.path.exists(deep_branch)
    assert os.path.isdir(deep_branch)

    assert os.path.exists(b_file_path)
    assert os.path.isfile(b_file_path)

    assert os.path.exists(third_added_file)
    assert os.path.isfile(third_added_file)


def test_adding_existing_file(bds, b_file, b_file_path):
    assert os.path.exists(b_file_path)
    assert os.path.isfile(b_file_path)

    path = bds.add_file(b_file)

    assert os.path.exists(path)
    assert os.path.isfile(path)


def test_adding_object_with_wrong_interface(bds):
    with pytest.raises(AssertionError):
        bds.add_file("hello")


def test_file_path_from_hash(bds, b_file_hash, b_file_path):
    assert bds.file_path_from_hash(b_file_hash) == b_file_path


def test_file_path_from_bad_hash(bds):
    with pytest.raises(IOError):
        bds.file_path_from_hash("azgabash")


def test_file_path_from_hash_subdirectory(bds, aa_file_hash, aa_file_path):
    assert bds.file_path_from_hash(aa_file_hash) == aa_file_path


def test_delete_by_file(bds, b_file, b_file_path):
    assert os.path.exists(b_file_path)
    assert os.path.isfile(b_file_path)

    bds.delete_by_file(b_file)

    assert not os.path.exists(b_file_path)
    assert not os.path.isfile(b_file_path)


def test_delete_unknown_path(bds):
    with pytest.raises(IOError):
        bds.delete_by_path("/azgabash")


def test_delete_unknown_existing_path(bds):
    with pytest.raises(IOError):
        bds.delete_by_path("/tmp")
