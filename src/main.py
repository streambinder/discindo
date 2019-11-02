#!/bin/env python3

import sys

from chopper.command import Command

if len(sys.argv) > 1 and sys.argv[1] == 'build':
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    Command.glue()
else:
    Command.chop()
