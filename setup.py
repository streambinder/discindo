#!/bin/env python3

from setuptools import setup, find_packages

setup(
    name='Discindo',
    version='4',
    # package_dir={'': 'discindo'},
    # packages=find_namespace_packages(where='discindo'),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'discindo = discindo.__main__:main'
        ]
    },
    author='Davide Pucci',
    author_email='discindo@davidepucci.it',
    description='Share all-sizes files using reconstructable manifests',
    keywords='storage file-sharing encryption',
    url='https://davidepucci.it/doc/discindo',
    license='GPL-3.0',
    project_urls={
        'Documentation': 'https://davidepucci.it/doc/discindo',
        'Source Code': 'https://github.com/streambinder/discindo',
        'Bug Tracker': 'https://github.com/streambinder/discindo/issues',
    },
    classifiers=[
        'License :: OSI Approved :: GPL-3.0'
    ]

)
