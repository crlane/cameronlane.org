#!/usr/bin/env python

from setuptools import (
    setup,
    find_packages
)

setup(
    name='blog-builder',
    version='1.0',
    description='A python app to build, deploy a simple static flask app',
    author='Cameron Lane',
    author_email='cameron@adamanteus.com',
    url='https://github.com/crlane/cameronlane.org',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=["Private :: Do Not Upload"],
    entry_points={
        'console_scripts': [
            'sitebuilder=builder.cli.sitebuilder:main',
        ]
    }
)
