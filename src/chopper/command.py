import argparse
import hashlib
import math
import ntpath
import os
import sys
import time

from .chop import Knife, Manifest
from .filesystem import File
from .provider import ThrottlingException
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

        if not os.path.isfile(args.filename):
            Command.print("File {} does not exist.".format(args.filename))
            sys.exit(1)

        args.filename = File(args.filename)
        os.chdir(args.filename.dir())

        if args.r > len(Storage.get_providers()):
            Command.print('Maximum redundancy level is {}: lowering it down.'.format(
                len(Storage.get_providers())))
            args.r = len(Storage.get_providers())

        Command.print('Going to chop file {} ({}) with level {} redundancy'.format(
            args.filename.base(), Command._nice_size_filename(args.filename.base()), args.r))
        knife = Knife(args.filename)

        chunks = []
        bytes_uploaded = 0
        throttling = dict()
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

                while p.nice_name() in throttling.keys() and int(time.time()) - throttling[p.nice_name()] < p.throttle():
                    Command.print('Provider {} is throttling: retrying later...'.format(
                        p.nice_name()), rev=True)
                    time.sleep(1)

                Command.print('[{}] Uploading {} on {}...'.format(Command._nice_size_value(bytes_uploaded),
                                                                  Command._nice_size_value(len(chunk)), p.nice_name()), rev=True)

                try:
                    chunk_uri = p.upload(chunk)
                    while chunk_uri is None:
                        Command.print(
                            'Unable to upload chunk: retrying...',  rev=True)
                        continue
                    chunk_uris.append(chunk_uri)
                    p_index += 1
                except ThrottlingException:
                    throttling[p.nice_name()] = int(time.time())
                    continue

            bytes_uploaded += len(chunk)
            chunks.append(
                {
                    'md5': hashlib.md5(chunk).hexdigest(),
                    'origins': chunk_uris
                }
            )

        Command.print('Uploaded {} chunks.'.format(len(chunks)))

        c = Manifest(chunks, args.filename.base(), args.filename.binary)
        Command.print('Generating chop file...', rev=True)
        c.persist()
        Command.print('Chop file generated: {} ({})'.format(
            c.filename_chop(), Command._nice_size_filename(c.filename_chop())))

    @staticmethod
    def glue():
        parser = Command.args_parser()
        parser.add_argument(
            'filename', help='Rebuild file using this chop file', type=str)
        args = parser.parse_args()

        if not os.path.isfile(args.filename):
            Command.print("File {} does not exist.".format(args.filename))
            sys.exit(1)

        args.filename = File(args.filename)
        os.chdir(args.filename.dir())

        Command.print('Going to rebuild chop file: {} ({})'.format(
            args.filename.base(), Command._nice_size_filename(args.filename.base())))
        c = Manifest.unpersist(args.filename.base())

        Command.print('Chop will merge {} chunks'.format(len(c.chunks)))
        chunk_data = []
        for chunk in c.chunks:
            for chunk_uri in chunk['origins']:
                provider = Storage.get_provider(chunk_uri)
                Command.print('Downloading chunk {} using {} provider...'.format(
                    len(chunk_data)+1, provider.nice_name()), rev=True)
                chunk_content = provider.download(chunk_uri)
                if hashlib.md5(chunk_content).hexdigest() != chunk['md5']:
                    Command.print(
                        'Chunk is corrupted: going to fetch from next origin.')
                    continue
                else:
                    chunk_data.append(chunk_content)
                    break
        Knife.merge(chunk_data, c.filename, c.binary)
        Command.print('Rebuilt original file into: {} ({})'.format(
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

    @staticmethod
    def print(*print_args, rev=False):
        sys.stdout.write('\033[2K\033[1G')
        if rev:
            print(*print_args, end='\r')
        else:
            print(*print_args)
