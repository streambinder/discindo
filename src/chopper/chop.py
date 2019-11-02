import base64
import json
import math
import ntpath
import os


class Knife():

    def __init__(self, filename):
        self.filename = filename
        self.source = open(filename, 'rb')
        self.source_offset = 0

    def chop(self, size):
        size *= 1024
        # the following calculation depends on encoding algorithm
        # base85 encoding always returns a payload which is 5 to 4
        # in proportion with the original payload
        size = math.floor(size / 5 * 4)
        self.source.seek(self.source_offset)
        chunk = base64.b85encode(self.source.read(size))
        self.source_offset += size
        return chunk if chunk != b'' else None

    @staticmethod
    def merge(chunks, filename):
        with open(filename, 'wb+') as fname:
            for chunk in chunks:
                fname.write(base64.b85decode(chunk))


class Manifest():

    EXTENSION = 'chop'

    def __init__(self, chunks, filename):
        self.chunks = chunks
        self.filename = ntpath.basename(filename)

    def filename_chop(self):
        return '{}.{}'.format(os.path.splitext(self.filename)[0], Manifest.EXTENSION)

    def serialize(self):
        return base64.b64encode(json.dumps(self.__dict__).encode('utf'))

    def persist(self):
        with open(self.filename_chop(), 'wb+') as payload:
            payload.write(self.serialize())

    @staticmethod
    def deserialize(payload):
        return Manifest(**json.loads(base64.b64decode(payload.decode())))

    @staticmethod
    def unpersist(filename):
        with open(filename, 'rb') as payload:
            return Manifest.deserialize(payload.read())
        return None
