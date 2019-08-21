import argparse
import hashlib
import math
import os
import time

from .chop import Knife, Manifest
from .provider import TrottlingException
from .storage import Storage


class Command():

    @staticmethod
    def args_parser():
        return argparse.ArgumentParser()

    @staticmethod
    def chop():
        parser = Command.args_parser()
        parser.add_argument(
            'filename', help='Generate chop for this file', type=str)
        args = parser.parse_args()

        print('Going to chop file: {} ({})'.format(
            args.filename, Command._nice_size_filename(args.filename)))
        knife = Knife(args.filename)

        chunks_uris = []
        bytes_uploaded = 0
        provider_trottling = dict()
        while True:
            provider = Storage.random_provider()
            if provider.nice_name() in provider_trottling.keys() and int(time.time()) - provider_trottling[provider.nice_name()] < provider.trottle():
                print('Provider {} is trottling: retrying later...'.format(
                    provider.nice_name()))
                continue

            chunk = knife.chop(provider.max_chunk_size())
            if chunk is None:
                break

            print('[{}] Uploading chunk {} using {} provider...'.format(Command._nice_size_value(bytes_uploaded + provider.max_chunk_size()),
                                                                        len(chunks_uris)+1, provider.nice_name()), end='\r')

            try:
                chunk_uri = provider.upload(chunk)
                if chunk_uri is None:
                    print('Unable to upload chunk: retrying...')
                    continue
                chunks_uris.append(chunk_uri)
                bytes_uploaded += len(chunk)
            except TrottlingException:
                print('Hit rate limit for {} provider: entering trottling mode and retrying with another provider...'.format(
                    provider.nice_name()))
                provider_trottling[provider.nice_name()] = int(time.time())
                continue
        print('Uploaded {} chunks.'.format(len(chunks_uris)))

        c = Manifest(chunks_uris, args.filename)
        print('Generating chop file...')
        c.persist()
        print('Chop file generated: {} ({})'.format(
            c.filename_chop(), Command._nice_size_filename(c.filename_chop())))

    @staticmethod
    def glue():
        parser = Command.args_parser()
        parser.add_argument(
            'filename', help='Rebuild file using this chop file', type=str)
        args = parser.parse_args()

        print('Going to rebuild chop file: {} ({})'.format(
            args.filename, Command._nice_size_filename(args.filename)))
        c = Manifest.unpersist(args.filename)

        print('Chop will merge {} chunks'.format(len(c.chunks)))
        chunk_data = []
        for uri in c.chunks:
            provider = Storage.get_provider(uri)
            print('Downloading chunk {} using {} provider...'.format(
                len(chunk_data)+1, provider.nice_name()), end='\r')
            chunk_data.append(provider.download(uri))
        Knife.merge(chunk_data, c.filename)
        print('Rebuilt original file into: {} ({})'.format(
            c.filename, Command._nice_size_filename(c.filename)))

    @staticmethod
    def _nice_size_filename(filename):
        return Command._nice_size_value(os.path.getsize(filename))

    @staticmethod
    def _nice_size_value(value, suffix='B'):
        magnitude = int(math.floor(math.log(value, 1024)))
        val = value / math.pow(1024, magnitude)
        if magnitude > 7:
            return '{:.1f}{}{}'.format(val, 'Yi', suffix)
        return '{:3.1f}{}{}'.format(val, ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z'][magnitude], suffix)
