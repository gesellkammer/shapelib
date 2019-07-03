#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='shapelib',
    version='0.1.0',
    description='Python utilities to facilitate working with shapely (shape creation, rasterization, plotting)',
    long_description=readme + '\n\n' + history,
    author='Eduardo Moguillansky',
    author_email='eduardo.moguillansky@gmail.com',
    url='https://github.com/gesellkammer/shapelib',
    packages=[
        'shapelib',
    ],
    package_dir={'shapelib':
                 'shapelib'},
    include_package_data=True,
    install_requires=[
        "numpy",
        "matplotlib",
        "shapely",
        "descartes",
        "rasterio"
    ],
    license="BSD",
    zip_safe=False,
    keywords='shapelib',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)