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
            'filename', type=str, help='Generate chop for this file')
        parser.add_argument(
            '-r', type=int, metavar='<value>', default=1, help='Set redundancy level (how many providers get used per chunk)')
        args = parser.parse_args()

        print('Going to chop file: {} ({})'.format(
            args.filename, Command._nice_size_filename(args.filename)))
        knife = Knife(args.filename)

        bytes_uploaded = 0
        chunks = []
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

            print('[{}] Uploading {} on {}...'.format(Command._nice_size_value(bytes_uploaded),
                                                      Command._nice_size_value(len(chunk)), provider.nice_name()), end='\r', flush=True)

            try:
                chunk_uri = provider.upload(chunk)
                if chunk_uri is None:
                    print('Unable to upload chunk: retrying...')
                    continue
                chunks.append(
                    {
                        'md5': hashlib.md5(chunk).hexdigest(),
                        'origins': [chunk_uri]
                    }
                )
                bytes_uploaded += len(chunk)
            except TrottlingException:
                print('Hit rate limit for {} provider: entering trottling mode and retrying with another provider...'.format(
                    provider.nice_name()))
                provider_trottling[provider.nice_name()] = int(time.time())
                continue
        print('Uploaded {} chunks.'.format(len(chunks)))

        c = Manifest(chunks, args.filename)
        print('Generating chop file...', end='\r')
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
        for chunk in c.chunks:
            for chunk_uri in chunk['origins']:
                provider = Storage.get_provider(chunk_uri)
                print('Downloading chunk {} using {} provider...'.format(
                    len(chunk_data)+1, provider.nice_name()), end='\r')
                chunk_content = provider.download(chunk_uri)
                if hashlib.md5(chunk_content).hexdigest() != chunk['md5']:
                    print('Chunk is corrupted: going to fetch from next origin.')
                    continue
                chunk_data.append(chunk_content)
        Knife.merge(chunk_data, c.filename)
        print('Rebuilt original file into: {} ({})'.format(
            c.filename, Command._nice_size_filename(c.filename)))

    @staticmethod
    def _nice_size_filename(filename):
        return Command._nice_size_value(os.path.getsize(filename))

    @staticmethod
    def _nice_size_value(value, suffix='B'):
        if value == 0:
            return '0.0B'
        magnitude = int(math.floor(math.log(value, 1024)))
        val = value / math.pow(1024, magnitude)
        if magnitude > 7:
            return '{:.1f}{}{}'.format(val, 'Yi', suffix)
        return '{:3.1f}{}{}'.format(val, ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z'][magnitude], suffix)
