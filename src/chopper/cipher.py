#!/bin/env python3

from itertools import cycle


class Cipher():

    @staticmethod
    def _xor(payload, key):
        if not isinstance(payload, bytes):
            raise Exception("not bytes")
        return ''.join([chr(c1 ^ ord(c2)) for (c1, c2) in zip(payload, cycle(key))]).encode()

    @staticmethod
    def encrypt(payload, key):
        return Cipher._xor(payload, key)

    @staticmethod
    def decrypt(payload, key):
        return Cipher._xor(payload, key)
