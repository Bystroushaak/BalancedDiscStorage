BalancedDiscStorage
===================

This module is used to provide storage for your files / archives. Storage itself makes sure, that there is never more files on one directory, than :attr:`.BalancedDiscStorage.dir_limit`.

:class:`.BalancedDiscStorage` accepts single files, :class:`.BalancedDiscStorageZ` whole directories packed using ZIP.

This class is necessary, because a lot of filesystems have problems with tens of thousands / milions files stored in one directory. This module stores the files in trees, which are similar to binary trees, but our trees should never change, once created. You can thus reference the returned paths in other software.

Usage example
-------------
Lets say, that we have some directory dedicated as file storage, for example ``/tmp/xex``. Lets also say, that we want maximally two files in one directory.

.. code-block:: python

    >>> from BalancedDiscStorage import BalancedDiscStorage
    >>> bds = BalancedDiscStorage("/tmp/xex", dir_limit=2)
    >>> bds
    BalancedDiscStorage(path='/tmp/xex', dir_limit=2)

We can now add the files. I have found two files, which hash starts with the letter ``a``. They are string ``38`` (hash ``aea92132c4cbeb263e6ac2bf6c183b5d81737f179f21efdc5863739672f0f470``) and ``318`` (hash ``aae02129362d611717b6c00ad8d73bf820a0f6d88fca8e515cafe78d3a335965``):

.. code-block:: python

    from StringIO import StringIO  # we will use "fake" files

    >>> bds.add_file(StringIO("38"))
    /tmp/xex/a/aea92132c4cbeb263e6ac2bf6c183b5d81737f179f21efdc5863739672f0f470_2
    >>> bds.add_file(StringIO("318"))
    /tmp/xex/a/aae02129362d611717b6c00ad8d73bf820a0f6d88fca8e515cafe78d3a335965_3

Now, lets look at the state of the filesystem::

    $ tree /tmp/xex
    /tmp/xex
    └── a
        ├── aae02129362d611717b6c00ad8d73bf820a0f6d88fca8e515cafe78d3a335965_3
        └── aea92132c4cbeb263e6ac2bf6c183b5d81737f179f21efdc5863739672f0f470_2

    1 directory, 2 files

As we can see, there are now two files in directory ``a/``. Thats correct, because we set the directory limit to ``2``. What will now happen, when we will add another file? Lets add „file“ ```391`` (hash ``a934c244755c66aebb0d6f9f5687038ffae8f00b00b28b4e17521016393f38b9``):

.. code-block:: python

    >>> p = bds.add_file(StringIO("391"))
    >>> p
    /tmp/xex/a/9/a934c244755c66aebb0d6f9f5687038ffae8f00b00b28b4e17521016393f38b9_3

As you can see from the example, file is now stored in subdirectory ``9``::

    $ tree /tmp/xex
    /tmp/xex
    └── a
        ├── 9
        │   └── a934c244755c66aebb0d6f9f5687038ffae8f00b00b28b4e17521016393f38b9_3
        ├── aae02129362d611717b6c00ad8d73bf820a0f6d88fca8e515cafe78d3a335965_3
        └── aea92132c4cbeb263e6ac2bf6c183b5d81737f179f21efdc5863739672f0f470_2

    2 directories, 3 files

This is how the :class:`.BalancedDiscStorage` balances the filesystem. Lets now look at the object returned from the :meth:`.add_file` call:

.. code-block:: python

    >>> type(p)
    <class 'BalancedDiscStorage.path_and_hash.PathAndHash'>
    >>> p.path
    '/tmp/xex/a/9/a934c244755c66aebb0d6f9f5687038ffae8f00b00b28b4e17521016393f38b9_3'
    >>> p.hash
    'a934c244755c66aebb0d6f9f5687038ffae8f00b00b28b4e17521016393f38b9_3'

Notice the :attr:`.hash` property, which may be used to delete (:meth:`.delete_by_hash`) the file:

.. code-block:: python

    >>> bds.delete_by_hash(p.hash)

As you can see, the file and also the directory was removed::

    $ tree /tmp/xex
    /tmp/xex
    └── a
        ├── aae02129362d611717b6c00ad8d73bf820a0f6d88fca8e515cafe78d3a335965_3
        └── aea92132c4cbeb263e6ac2bf6c183b5d81737f179f21efdc5863739672f0f470_2

    1 directory, 2 files

You can of course delete the file also by full path (:meth:`.delete_by_path`):

.. code-block:: python

    >>> bds.delete_by_path("/tmp/xex/a/aae02129362d611717b6c00ad8d73bf820a0f6d88fca8e515cafe78d3a335965_3")

::

    $ tree /tmp/xex
    /tmp/xex
    └── a
        └── aea92132c4cbeb263e6ac2bf6c183b5d81737f179f21efdc5863739672f0f470_2

    1 directory, 1 file

Or by original file object:

.. code-block:: python

    >>> bds.delete_by_file(StringIO("38"))

::

    $ tree /tmp/xex
    /tmp/xex

    0 directories, 0 files

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
