import argparse
import hashlib
import math
import os
import sys
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

        if args.r > len(Storage.get_providers()):
            print('Maximum redundancy level is {}: lowering it down.'.format(
                len(Storage.get_providers())))
            args.r = len(Storage.get_providers())

        print('Going to chop file {} ({}) with level {} redundancy'.format(
            args.filename, Command._nice_size_filename(args.filename), args.r))
        knife = Knife(args.filename)

        chunks = []
        bytes_uploaded = 0
        trottling = dict()
        while True:
            providers = Storage.random_provider(size=args.r)
            chunk_size = Storage.providers_chunk_size(providers)
            chunk_uris = []
            chunk = knife.chop(chunk_size)

            if chunk is None:
                break

            p_index = 0
            while p_index < len(providers):
                p = providers[p_index]

                while p.nice_name() in trottling.keys() and int(time.time()) - trottling[p.nice_name()] < p.trottle():
                    print('Provider {} is trottling: retrying later...'.format(
                        p.nice_name()), end='\r', flush=True)
                    time.sleep(1)

                print('[{}] Uploading {} on {}...'.format(Command._nice_size_value(bytes_uploaded),
                                                          Command._nice_size_value(len(chunk)), p.nice_name()), end='\r', flush=True)

                try:
                    chunk_uri = p.upload(chunk)
                    while chunk_uri is None:
                        print('Unable to upload chunk: retrying...',  end='\r')
                        continue
                    chunk_uris.append(chunk_uri)
                    p_index += 1
                except TrottlingException:
                    trottling[p.nice_name()] = int(time.time())
                    continue

            bytes_uploaded += len(chunk)
            chunks.append(
                {
                    'md5': hashlib.md5(chunk).hexdigest(),
                    'origins': chunk_uris
                }
            )

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
                else:
                    chunk_data.append(chunk_content)
                    break
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
