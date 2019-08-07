#!/bin/env python3


class abstatic(staticmethod):
    __slots__ = ()

    def __init__(self, function):
        super(abstatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True
