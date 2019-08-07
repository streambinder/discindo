import abc
import importlib
import json
import os
import pkgutil
import random
import re
import requests
import sys

from os import listdir
from os.path import isfile, join
from .storage.generic import ChunkStorage


class StorageProvider():

    providers = None

    @staticmethod
    def get_providers():
        if StorageProvider.providers is not None:
            return StorageProvider.providers

        StorageProvider.providers = list()

        providers_path = '{}/storage'.format(
            os.path.dirname(os.path.realpath(__file__)))
        for f in listdir(providers_path):
            if re.search(r'^(?!__).*\.py$', f) is not None:
                importlib.import_module(
                    'chopper.storage.{}'.format(f.replace('.py', '')))
        StorageProvider.providers = ChunkStorage.__subclasses__()
        return StorageProvider.providers

    @staticmethod
    def get_provider(uri):
        for provider in StorageProvider.get_providers():
            if provider.is_supporting(uri):
                # next line validates provider to check
                # if it implements all the abstract methods
                try:
                    provider()
                except TypeError as e:
                    if re.search(r'^.*with\sabstract\smethods\s.*$', str(e)) is not None:
                        raise TypeError('Unimplemented ChunkStorage methods: {}'.format(
                            str(e).split("methods ")[1]))
                    else:
                        raise e
                return provider
        return None

    @staticmethod
    def random_provider():
        while True:
            provider = random.choice(StorageProvider.get_providers())
            try:
                provider()
                return provider
            except:
                pass
