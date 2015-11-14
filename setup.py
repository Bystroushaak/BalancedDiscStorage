#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup, find_packages

from docs import getVersion


# Variables ===================================================================
CHANGELOG = open('CHANGELOG.rst').read()
LONG_DESCRIPTION = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    CHANGELOG
])


# Actual setup definition =====================================================
setup(
    name='BalancedDiscStorage',
    version=getVersion(CHANGELOG),
    description=(
        "Makes sure, that there are never more files in one directory, than "
        "your LIMIT."
    ),
    long_description=LONG_DESCRIPTION,
    url='https://github.com/Bystroushaak/BalancedDiscStorage',

    author='Bystroushaak',
    author_email='bystrousak@kitakitsune.org',

    classifiers=[
        "Development Status :: 3 - Alpha",

        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",

        "License :: OSI Approved :: MIT License",
    ],
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    include_package_data=True,
    zip_safe=False,

    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    }
)
