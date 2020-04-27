#!/bin/env python3

import sys

from .command import Command


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        Command.glue()
    else:
        Command.chop()


if __name__ == '__main__':
    main()
