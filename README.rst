Introduction
============

.. image:: https://badge.fury.io/py/BalancedDiscStorage.png
    :target: https://pypi.python.org/pypi/BalancedDiscStorage

.. image:: https://img.shields.io/pypi/dm/BalancedDiscStorage.svg
    :target: https://pypi.python.org/pypi/BalancedDiscStorage

.. image:: https://readthedocs.org/projects/balanceddiscstorage/badge/?version=latest
    :target: http://balanceddiscstorage.readthedocs.org/
    
.. image:: https://img.shields.io/github/issues/Bystroushaak/BalancedDiscStorage.svg
    :target: https://github.com/Bystroushaak/BalancedDiscStorage/issues

.. image:: https://img.shields.io/pypi/l/BalancedDiscStorage.svg

This module is used to provide storage for your files / archives. Storage itself makes sure, that there is never more files in one directory, than ``BalancedDiscStorage.dir_limit``.

This module is necessary, because a lot of filesystems have problems with tens of thousands / milions files stored in one directory. This module stores the files in trees, which are similar to binary trees, but our trees should never change, once created. You can thus reference the returned paths in other software.

Documentation
-------------

Full module documentation and description can be found at Read the Docs:

- http://balanceddiscstorage.rtfd.org
