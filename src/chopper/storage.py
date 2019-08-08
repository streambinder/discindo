import abc
import importlib
import json
import os
import pkgutil
import random
import re
import sys
from os import listdir
from os.path import isfile, join

import requests

from .provider import Provider


class Storage():

    providers = None

    @staticmethod
    def get_providers():
        if Storage.providers is not None:
            return list(Storage.providers)

        Storage.providers = list()

        try:
            providers_path = '{}/providers'.format(
                os.path.dirname(os.path.realpath(__file__)))
            for f in listdir(providers_path):
                if re.search(r'^(?!__).*\.py$', f) is not None:
                    importlib.import_module(
                        'chopper.providers.{}'.format(f.replace('.py', '')))
        except:
            pass
        Storage.providers = Provider.__subclasses__()
        return Storage.providers

    @staticmethod
    def get_provider(uri):
        for provider in Storage.get_providers():
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
            provider = random.choice(Storage.get_providers())
            try:
                provider()
                return provider
            except:
                pass
