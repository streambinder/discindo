import argparse
import hashlib
import math
import os

from .chop import Knife, Manifest
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
        provider = Storage.random_provider()
        chunk = knife.chop(provider.max_chunk_size())
        while chunk is not None:
            print('Uploading chunk {} using {} provider...'.format(
                len(chunks_uris)+1, provider.nice_name()), end='\r')
            chunks_uris.append(provider.upload(chunk))
            provider = Storage.random_provider()
            chunk = knife.chop(provider.max_chunk_size())
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
        return '{:3.1f}{}{}'.format(val, ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi'][magnitude], suffix)
