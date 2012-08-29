#!/usr/bin/env python
"""Command line wrapper for the ServerDensity API
"""

import os
import sys
from optparse import OptionParser
from clint import resources
from clint.textui import puts, colored, indent
from serverdensity.api import SDApi

try:
    # Try simplejson first as it has speed advantages over std lib
    import simplejson as json
except ImportError:
    import json

def main():
    """Main console script entrypoint for densli app

    Returns an integer POSIX exit code.
    """

    resources.init('ServerDensity', 'Densli')

    config_path = os.getenv('DENSLI_HOME', False)
    if config_path:
        puts(colored.yellow('Using "%s" from DENSLI_HOME env var..' %
            (config_path,)))

        resources.user.path = os.path.expanduser(config_path)
        resources.user._exists = False
        resources.user._create()

    config = resources.user.read('config.json')

    if config is None:
        with open(os.path.join(os.path.dirname(__file__), 'config.json')) as json_fp:
            resources.user.write('config.json', json_fp.read())

        fp = resources.user.open('config.json')

        with indent(4, quote='>>>'):
            puts(colored.red('No config.json found..'))
            puts(colored.red('Initialised basic config.json at: %s' %
                             (os.path.abspath(fp.name),)))
            puts(colored.red('Edit this file and fill in your SD API details.'))

        fp.close()
        return 1

    try:
        config = json.loads(config)
    except Exception, e:
        with indent(4, quote='>>>'):
            puts(colored.red('Error parsing JSON from config file:'))
            puts('')
        with indent(8, quote='>>>'):
            puts(colored.red(unicode(e)))
        return 1


    return 0


if __name__ == '__main__':
    sys.exit(main())
