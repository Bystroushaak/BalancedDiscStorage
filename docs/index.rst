BalancedDiscStorage
===================

This module is used to provide storage for your files / archives. Storage itself makes sure, that there is never more files on one directory, than :attr:`.BalancedDiscStorage.dir_limit`.

Storage accepts single files, or whole directories packed using ZIP.

..
    Package structure
    -----------------

    Class relations
    +++++++++++++++

API
---
:doc:`/api/BalancedDiscStorage`:

.. toctree::
    :maxdepth: 1

    /api/balanced_disc_storage
    /api/balanced_disc_storage_z
    /api/path_and_hash

Installation
------------
Module is hosted at `PYPI <https://pypi.python.org/pypi/BalancedDiscStorage>`_,
and can be easily installed using `PIP`_::

    sudo pip install BalancedDiscStorage

.. _PIP: http://en.wikipedia.org/wiki/Pip_%28package_manager%29

Source code
+++++++++++
Project is released under the MIT license. Source code can be found at GitHub:

- https://github.com/Bystroushaak/BalancedDiscStorage

Unittests
+++++++++
Almost every feature of the project is tested by unittests. You can run those
tests using provided ``run_tests.sh`` script, which can be found in the root
of the project.

If you have any trouble, just add ``--pdb`` switch at the end of your ``run_tests.sh`` command like this: ``./run_tests.sh --pdb``. This will drop you to `PDB`_ shell.

.. _PDB: https://docs.python.org/2/library/pdb.html

Example
^^^^^^^
::

    ./run_tests.sh 
    ============================= test session starts ==============================
    platform linux2 -- Python 2.7.6 -- py-1.4.30 -- pytest-2.7.2
    rootdir: /home/bystrousak/Plocha/Dropbox/c0d3z/prace/BalancedDiscStorage/tests, inifile: 
    plugins: cov
    collected 22 items 

    tests/test_a_path_and_hash.py ..
    tests/test_balanced_disc_storage.py ..............
    tests/test_balanced_disc_storagez.py ......

    ========================== 22 passed in 0.04 seconds ===========================


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
