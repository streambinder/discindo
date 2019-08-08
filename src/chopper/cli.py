import argparse
import hashlib

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
        knife = Knife(args.filename)
        print('Chopping file: {}'.format(args.filename))

        provider = Storage.random_provider()
        print('Provider chosen: {}'.format(provider))

        chunks_uris = []
        chunk = knife.chop(provider.max_chunk_size())
        while chunk is not None:
            print('Uploading chunk: #{}/{}'.format(len(chunk),
                                                   hashlib.md5(chunk).hexdigest()))
            uri = provider.upload(chunk)
            print('Uploaded: {}'.format(uri))
            chunks_uris.append(uri)
            chunk = knife.chop(provider.max_chunk_size())
        print('Uploaded all chunks: {}'.format(len(chunks_uris)))

        c = Manifest(chunks_uris, args.filename)
        print('Creating chop file: {}'.format(c.filename_chop()))
        c.persist()

    @staticmethod
    def glue():
        parser = Command.args_parser()
        parser.add_argument(
            'filename', help='Generate chop for this file', type=str)
        args = parser.parse_args()
        print('Reading chop file: {}'.format(args.filename))
        c = Manifest.unpersist(args.filename)
        Knife.merge([Storage.get_provider(uri).download(uri)
                     for uri in c.chunks], c.filename)
        print('Merged chunks into file: {}'.format(c.filename))
