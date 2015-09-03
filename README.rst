BalancedDiscStorage
===================

.. image:: https://badge.fury.io/py/BalancedDiscStorage.png
    :target: https://pypi.python.org/pypi/BalancedDiscStorage

.. image:: https://img.shields.io/pypi/dm/BalancedDiscStorage.svg
    :target: https://pypi.python.org/pypi/BalancedDiscStorage

.. image:: https://readthedocs.org/projects/BalancedDiscStorage/badge/?version=latest
    :target: http://BalancedDiscStorage.readthedocs.org/

.. image:: https://img.shields.io/pypi/l/BalancedDiscStorage.svg

.. image:: https://img.shields.io/github/issues/edeposit/BalancedDiscStorage.svg
    :target: https://github.com/edeposit/BalancedDiscStorage/issues

This module is used to provide storage for your files / archives. Storage itself makes sure, that there is never more files on one directory, than :attr:`.BalancedDiscStorage.dir_limit`.

This module is necessary, because a lot of filesystems have problems with tens of thousands / milions files stored in one directory. This module stores the files in trees, which are similar to binary trees, but our trees should never change, once created. You can thus reference the returned paths in other software.

Documentation
-------------

Full module documentation and description can be found at Read the Docs:

- http://balanceddiscstorage.rtfd.org