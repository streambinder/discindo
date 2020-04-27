#!/bin/env python3

from setuptools import setup, find_packages

setup(
    name='Chopper',
    version='2',
    # package_dir={'': 'chopper'},
    # packages=find_namespace_packages(where='chopper'),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'chopper = chopper.__main__:main'
        ]
    },
    author='Davide Pucci',
    author_email='chopper@davidepucci.it',
    description='Share all-sizes files using reconstructable manifests',
    keywords='storage file-sharing encryption',
    url='https://davidepucci.it/doc/chopper',
    license='GPL-3.0',
    project_urls={
        'Documentation': 'https://davidepucci.it/doc/chopper',
        'Source Code': 'https://github.com/streambinder/chopper',
        'Bug Tracker': 'https://github.com/streambinder/chopper/issues',
    },
    classifiers=[
        'License :: OSI Approved :: GPL-3.0'
    ]

)
