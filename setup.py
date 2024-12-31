#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import find_packages, setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-baseline',
    version='0.1.0',
    author='Keith Knapp',
    author_email='keith.knapp@slalom.com',
    maintainer='Keith Knapp',
    maintainer_email='keith.knapp@slalom.com',
    license='MIT',
    url='https://github.com/knappkeith/pytest-baseline',
    description='A plugin to accelerate writing highly repeatable tests',
    long_description=read('README.md'),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires='>=3.5',
    install_requires=[
        'pytest>=7.1.2',
        "pytest-html==4.1.0"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'baseline = pytest_baseline.plugin',
        ],
    },
)
