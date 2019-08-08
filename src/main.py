#!/bin/env python3

import argparse
import hashlib

from chopper.chop import Knife, Manifest
from chopper.storage import Storage

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--reconstruct',
                    help='Switch to reconstruct mode', action='store_true')
parser.add_argument('filename', help='Operate over this filename', type=str)
args = parser.parse_args()

if not args.reconstruct:
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
else:
    print('Reading chop file: {}'.format(args.filename))
    c = Manifest.unpersist(args.filename)
    Knife.merge([Storage.get_provider(uri).download(uri)
                 for uri in c.chunks], c.filename)
    print('Merged chunks into file: {}'.format(c.filename))
