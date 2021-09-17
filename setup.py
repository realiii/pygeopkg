#!/usr/bin/env python

from setuptools import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='pygeopkg',
    version='0.1',
    # author='Author',
    # author_email='author@email.com',
    description='A Python library that allows for the creation and population of OGC GeoPackage databases with write access',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/realiii/pygeopkg',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        # 'Development Status :: 5 - Production/Stable',
    ],
    packages=['conversion', 'core', 'resources', 'shared'],
)
