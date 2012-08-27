#!/usr/bin/env python
"""Command line wrapper for the ServerDensity API
"""

import os
import sys
from optparse import OptionParser
from clint import resources
from clint.textui import puts, colored, indent
from serverdensity.api import SDApi

resources.init('ServerDensity', 'densli')
config = resources.user.read('config.ini')

if config is None:
    resources.user.write('config.ini', 'BASIC CONFIG HERE')
    fp = resources.user.open('config.ini')

    with indent(4, quote='>>>'):
        puts(colored.red('No config.ini found..'))
        puts(colored.red('Initialised basic config.ini at: %s' %
                         (os.path.abspath(fp.name),)))
        puts(colored.red('Edit this file and fill in your SD API details.'))

    fp.close()
    sys.exit(78)


sys.exit(0)
