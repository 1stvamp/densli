#!/usr/bin/env python
"""Command line wrapper for the ServerDensity API
"""

import os
import sys
from optparse import OptionParser
from clint import resources
from clint.textui import puts, colored, indent
from serverdensity.api import SDApi

STDERR = sys.stderr.write

try:
    # Try simplejson first as it has speed advantages over std lib
    import simplejson as json
except ImportError:
    import json

def main():
    """Main console script entrypoint for densli app

    Returns an integer POSIX exit code.
    """

    parser = OptionParser(usage="""usage: %prog [options]""")
    parser.add_option("-u", "--username", dest="username", help="Optional SD"
                      " username, overrides config file")
    parser.add_option("-p", "--password", dest="password", help="Optional SD"
                      " password, overrides config file")
    parser.add_option("-a", "--account", dest="account", help="SD account"
                      ", overrides config file (optional)")
    parser.add_option("-q", "--quiet", dest="quiet", help="Don't output"
                      " feedback to stdout", action="store_true")

    (options, args) = parser.parse_args()

    resources.init('ServerDensity', 'Densli')

    # Allow the user to override the location for config files with an
    # environment variable
    config_path = os.getenv('DENSLI_HOME', False)
    if config_path:
        if not options.quiet:
            with indent(4, '>>>'):
                puts(colored.yellow('Using "%s" from DENSLI_HOME env var..' %
                                    (config_path,)))

        resources.user.path = os.path.expanduser(config_path)
        resources.user._exists = False
        resources.user._create()

    config = resources.user.read('config.json')

    # If we couldn't load a config, create a default config file but warn
    # the user as it won't work without editing
    if config is None:
        with open(os.path.join(os.path.dirname(__file__), 'config.json')) as json_fp:
            resources.user.write('config.json', json_fp.read())

        fp = resources.user.open('config.json')

        with indent(4, quote='!!!'):
            puts(colored.red('No config.json found..'), stream=STDERR)
            puts(colored.red('Initialised basic config.json at: %s' %
                             (os.path.abspath(fp.name),)), stream=STDERR)
            puts(colored.red('Edit this file and fill in your SD API'
                              ' details.'), stream=STDERR)
            puts(colored.red('Remember to remove the "enabled" field or set it'
                             ' to true.'), stream=STDERR)

        fp.close()
        return 1

    # Load JSON and handle decoding errors
    try:
        config = json.loads(config)
    except Exception, e:
        with indent(4, quote='!!!'):
            puts(colored.red('Error parsing JSON from config file:'),
                             stream=STDERR)
            puts('', stream=STDERR)
        with indent(8, quote='!!!'):
            puts(colored.red(unicode(e)), stream=STDERR)
        return 1

    if not config.get('enabled', True):
        # User either hasn't edited or hasn't enabled their default config file
        with indent(4, quote='!!!'):
                puts(colored.red('Config file disabled!'), stream=STDERR)
                puts(colored.red('Have you edited your config file?'),
                                 stream=STDERR)
                puts(colored.red('If so remove the "enabled" field or set it'
                                 ' to true.'), stream=STDERR)
        return 1

    if not args:
        with indent(4, '!!!'):
            puts(colored.red('No arguments supplied, please give me a path to'
                            ' actually retrieve from the SD API.'))
        return 1

    if options.username:
        config['username'] = options.username
    if options.password:
        config['password'] = options.password
    if options.account:
        config['account'] = options.account

    api = SDApi(**config)

    return 0


if __name__ == '__main__':
    sys.exit(main())
