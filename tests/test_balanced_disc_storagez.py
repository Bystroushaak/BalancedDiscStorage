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

from BalancedDiscStorage import BalancedDiscStorageZ

from test_balanced_disc_storage import data_file_context


# Variables ===================================================================
TEMP_DIR = None


# Fixtures ====================================================================
@pytest.fixture
def bdsz():
    return BalancedDiscStorageZ(TEMP_DIR)


@pytest.fixture
def archive_file():
    return data_file_context("archive.zip")


@pytest.fixture
def archive_file_hash():
    return "b5770bf1233f932fb5d5729a07fc786e3040bcdbe528b70a4ad2cbc3b6eb2380_12d"


@pytest.fixture
def archive_file_path():
    file_hash = archive_file_hash()

    return join(TEMP_DIR, file_hash[0], file_hash) + "/"


@pytest.fixture
def archive_filenames():
    return [
        join(archive_file_path(), fn)
        for fn in ["metadata.xml", "some.pdf"]
    ]


# Setup =======================================================================
def setup_module():
    global TEMP_DIR

    TEMP_DIR = tempfile.mkdtemp()


def teardown_module():
    shutil.rmtree(TEMP_DIR)


# Tests =======================================================================
def test_init():
    bdsz = BalancedDiscStorageZ(TEMP_DIR)

    with pytest.raises(TypeError):
        BalancedDiscStorageZ()


def test_add_archive_as_dir(bdsz, archive_file, archive_file_hash,
                            archive_file_path, archive_filenames):
    bdsz.dir_limit = 20
    assert not os.path.exists(archive_file_path)

    bdsz.add_archive_as_dir(archive_file)

    assert os.path.exists(archive_file_path)
    assert os.path.isdir(archive_file_path)

    for filename in archive_filenames:
        assert os.path.exists(filename)
        assert os.path.isfile(filename)


def test_add_archie_twice(bdsz, archive_file, archive_file_hash,
                          archive_file_path, archive_filenames):
    bdsz.add_archive_as_dir(archive_file)
    bdsz.add_archive_as_dir(archive_file)

    assert os.path.exists(archive_file_path)
    assert os.path.isdir(archive_file_path)

    for filename in archive_filenames:
        assert os.path.exists(filename)
        assert os.path.isfile(filename)


def test_too_many_zip_files(bdsz, archive_file):
    max_zipfiles = bdsz.max_zipfiles
    bdsz.max_zipfiles = 1

    with pytest.raises(ValueError):
        bdsz.add_archive_as_dir(archive_file)

    bdsz._max_zipfiles = max_zipfiles


def test_path_from_hash_for_zip(bdsz, archive_file_path, archive_file_hash):
    assert bdsz.file_path_from_hash(archive_file_hash) == archive_file_path


def test_delete_by_file_zip(bdsz, archive_file, archive_file_path):
    assert os.path.exists(archive_file_path)
    assert os.path.isdir(archive_file_path)

    bdsz.delete_by_file(archive_file)

    assert not os.path.exists(archive_file_path)
    assert not os.path.isdir(archive_file_path)

    # check that blank directories are also cleaned
    assert not os.path.exists(join(TEMP_DIR, "b"))
################################################################################
# WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARN #
# DO NOT PUT MORE TESTS AFTER THIS TEST - PYTEST IS BROKEN AND SO WILL BE YOUR #
# CODE                                                                         #
################################################################################