import ntpath
import os

from pathlib import Path


class File():

    def __init__(self, filename):
        self._fname = filename
        self.binary = File._guess_binary(filename)

    @staticmethod
    def _guess_binary(filename):
        textchars = bytearray({7, 8, 9, 10, 12, 13, 27}
                              | set(range(0x20, 0x100)) - {0x7f})
        return bool(open(filename, 'rb').read(1024).translate(None, textchars))

    @staticmethod
    def pretty(filename):
        return filename.replace(str(Path.home()), "~")

    def dir(self):
        return os.path.dirname(self._fname) or '.'

    def base(self):
        return ntpath.basename(self._fname)

    def full(self):
        return "{}{}{}".format(self.dir(), os.sep, self.base())
