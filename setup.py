#!/usr/bin/env python

# This file is part of metamodule
# Copyright (C) 2015 Nathaniel Smith <njs@pobox.com>
# See file LICENSE for license information.

import sys
from setuptools import setup

DESC = """A tiny Python module that lets you take more control of your
library's public API."""

LONG_DESC = open("README.rst").read()

# For __version__ and __doc__
import metamodule

setup(
    name="metamodule",
    version=metamodule.__version__,
    description=metamodule.__doc__,
    long_description=LONG_DESC,
    author="Nathaniel J. Smith",
    author_email="njs@pobox.com",
    license="2-clause BSD",
    py_modules=["metamodule"],
    url="https://github.com/njsmith/metamodule",
    classifiers =
      [ "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
