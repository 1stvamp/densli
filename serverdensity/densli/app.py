#!/usr/bin/env python
"""Command line wrapper for the ServerDensity API
"""

from __future__ import division

import os
import re
import sys
from itertools import islice
from optparse import OptionParser
from datetime import timedelta, datetime

from clint import resources, piped_in
from clint.textui import puts, colored, indent, columns
from serverdensity.api import SDApi, SDServiceError
from sparkblocks import spark

STDERR = sys.stderr.write

try:
    # Try simplejson first as it has speed advantages over std lib
    import simplejson as json
except ImportError:
    import json


def show_error(msgs, ex=None, tab=4):
    for msg in msgs:
        with indent(tab, quote='!!!'):
            puts(colored.red(msg), stream=STDERR)

    if ex:
        puts('', stream=STDERR)
        with indent(8, quote='!!!'):
            puts(colored.red(unicode(ex)), stream=STDERR)


def show_info(msgs):
    for msg in msgs:
        with indent(4, '>>>'):
            puts(colored.yellow(msg))


def main():
    """Main console script entrypoint for densli app

    Returns an integer exit code 0 for success, 1 for error(s).
    """

    parser = OptionParser(usage="""usage: %prog [options] thing method""")

    parser.add_option("-u", "--username", dest="username", help="SD username"
                      ", overrides config file.")

    parser.add_option("-p", "--password", dest="password", help="SD password"
                      ", overrides config file.")

    parser.add_option("-a", "--account", dest="account", help="SD account"
                      ", overrides config file.")

    parser.add_option("-q", "--quiet", dest="quiet", help="Don't output"
                      " feedback to stdout.", action="store_true")

    parser.add_option("-s", "--spark", dest="spark", help="Generate a text"
                      " based sparkline graph from metrics.getRange results.",
                      action="store_true")

    parser.add_option("-P", "--postback", dest="postback", help="Flag STDIN"
                      " piped data as being a metric postback, so send as raw"
                      " JSON in the POST field 'postback'.",
                      action="store_true")

    parser.add_option("-t", "--timeago", dest="timeago", help="Take a relative"
                      " time offset from NOW and use that as the range for"
                      " a metrics.getRange call. Accepts [Nd[ay]] [Nh[our]]"
                      " [Nm[in[utes]]] [Ns[ec[ond]]] in any combination, e.g."
                      " 1h 20sec, 5min, 2day 15s, 12 minutes etc.")

    parser.add_option("-d", "--data", dest="data", help="Data to send to"
                      " the API. Multiple data values are excepted. Values"
                      " should be in name/value pairs, e.g. name=value",
                      action="append", default=[])

    (options, args) = parser.parse_args()

    resources.init('ServerDensity', 'Densli')

    # Allow the user to override the location for config files with an
    # environment variable
    config_path = os.getenv('DENSLI_HOME', False)
    if config_path:
        if not options.quiet:
            show_info(['Using "%s" from DENSLI_HOME env var..' %
                       (config_path,)])

        resources.user.path = os.path.expanduser(config_path)
        resources.user._exists = False
        resources.user._create()

    config = resources.user.read('config.json')

    # If we couldn't load a config, create a default config file but warn
    # the user as it won't work without editing
    if config is None:
        with open(os.path.join(
                os.path.dirname(__file__), 'config.json')) as json_fp:
            resources.user.write('config.json', json_fp.read())

        fp = resources.user.open('config.json')

        show_error(['No config.json found..',
                    'Initialised basic config.json at: %s' %
                     (os.path.abspath(fp.name),),
                    'Edit this file and fill in your SD API details.',
                    'Remember to remove the "enabled" field or set it to'
                    ' true.'])

        fp.close()
        return 1

    # Load JSON and handle decoding errors
    try:
        config = json.loads(config)
    except Exception, e:
        show_error(['Error parsing JSON from config file:'], e)
        return 1

    if not config.get('enabled', True):
        # User either hasn't edited or hasn't enabled their default config file
        show_error(['Config file disabled!',
                    'Have you edited your config file?',
                    'If so remove the "enabled" field or set it to true.'])
        return 1

    # If we didn't get any args of we got a single arg but it didn't contain a
    # recognised delimiter, then we can't proceed as we don't know what to get
    # from the API
    if not args or (len(args) == 1
            and not any(x in args[0] for x in ('/', '.'))):
        show_error(['Too few arguments supplied, please give me a full'
                     ' path to actually retrieve from the SD API.',
                     'Path can be in any of the form:'])

        show_error(['thing method',
                    'thing/method',
                    'thing.method'], tab=8)

        return 1

    # Override values from config file with CLI options
    if options.username:
        config['username'] = options.username
    if options.password:
        config['password'] = options.password
    if options.account:
        config['account'] = options.account

    api = SDApi(account=config['account'], username=config['username'],
                password=config['password'])

    # Turn alternative API path formats into a usable list, e.g.
    # thing.method into ['thing', 'method]
    if any(x in args[0] for x in ('/', '.')):
        delim = '.' if '.' in args[0] else '/'
        args[:1] = args[0].split(delim)

    # Allow request data as trailing args
    if len(args) > 2:
        options.data[:0] = args[2:]
        args = args[0:2]

    # Turn multiple name=value -d/--data options into a dict
    data = {}
    if len(options.data) > 0:
        try:
            data = dict(d.split('=') for d in options.data)
        except ValueError, e:
            show_error(['Data (-d/--data) parsing error.',
                        'Remember they must be in name/value pairs, e.g.'
                         ' -d name=value'], e)
            return 1

    # Check for piped in data
    piped_data = piped_in()
    if piped_data:
        if options.postback:
            # Treat STDIN as a raw JSON string to send in postback field
            data['postback'] = piped_in
        else:
            try:
                data.update(json.loads(piped_data))
            except Exception, e:
                show_error(['Error parsing data from stdin.'], e)
                return 1

    # Parse relative date range offset for metrics.getRange calls
    if options.timeago:
        part_names = ['days', 'hours', 'minutes', 'seconds']
        parts = {}
        for name in part_names:
            result = re.search('(?P<%s>\d+)\s*?[%s]' % (name, name[0]),
                               options.timeago)
            if result:
                parts[name] = int(result.group(name))

        range_end = datetime.utcnow().replace(microsecond=0)
        range_start = range_end - timedelta(**parts)

        data['rangeStart'] = str(range_start)
        data['rangeEnd'] = str(range_end)

    curr = api
    for arg in args:
        curr = getattr(curr, arg)

    error = False
    try:
        api_output = curr(data)['data'][args[0]]
    except SDServiceError, e:
        api_output = e.response
        error = True
    except Exception, e:
        show_error(['Something went wrong sending the API request:'], e)
        return 1

    if (not error and args[0] == 'metrics' and args[1] == 'getRange' and
            options.spark):
        for k, metrics in api_output.iteritems():
            # Hack to get around some metrics data structures returned by the
            # API having subkeys
            if 'label' in metrics:
                metrics = {'': metrics}

            for _, metric in metrics.iteritems():
                show_info(["%s for %s - %s:" % (metric['label'],
                                                data['rangeStart'],
                                                data['rangeEnd'])])

                values = [v[1] for v in metric['data']]

                # Anything bigger than this looks like crap in the terminal
                max_graph_width = config.get('max_graph_width', 20)
                if len(values) > max_graph_width:
                    slice_value = int(len(values) / max_graph_width)

                    # Reduce large list to smaller list of averages
                    # by taking mean of sliding window normalised lists
                    # for every X normalised list (not entirely accurate,
                    # but good enough)
                    values = list(sum(values[i:i + slice_value]) / len(values)
                                  for i in xrange(len(values) - 2)
                                           if i % slice_value == 0)

                puts(colored.blue(spark(values)))
    else:
        puts(json.dumps(api_output, indent=4))

    return 0


if __name__ == '__main__':
    sys.exit(main())
