densli
======

About densli
------------
``densli`` is a command line client for accessing the `Server Density <http://www.serverdensity.com>`_ `API <https://github.com/serverdensity/sd-api-docs>`_ with the following features:

 * Store authentication details in a config file, or pass them as command options
 * Extensive error checking
 * Display metric ranges as a sparklines graph
 * Pretty ``TERM`` colours!
 * Outputs JSON in an indented human readable (but still machine readable) format
 * Can accept data to send as JSON via piped ``stdin``
 * Suppress none JSON data output via option to pipe data to other processes
 * Flexible ways to define API endpoints and data to send (different API path formats and add data via ``stdin``, named options or as extra unnamed arguments)

Installation
------------
The app can be installed from PyPi using ``pip``::

    pip install densli

Or cloned from `Github <http://www.github.com/>`_ using ``git``::

    git clone git://github.com/serverdensity/densli.git
    cd densli
    python setup.py install

Usage
-----
densli uses a JSON config file to store authentication info (account / username / passord), and other options.
To create an example config file you can edit with your SD details just run
``densli`` for the first time, it will report where it has created the config
file (this is usually in a standard location for configurations for your
operating system, e.g. under ``$HOME/Library/Application Support/Densli`` under OS X).
The location for this config file can be changed using the environment variable ``DENSLI_HOME``, e.g.::

    DENSLI_HOME=~/.densli
    export DENSLI_HOME
    densli ...

Any or all of the auth details can be overridden as options passed to densli, this is useful for running from scripts where you don't want to keep your auth details stored in a file, e.g.::

    densli --username=myusername --password=mypassword --account=myaccount.serverdensity.com ...

You can get a list/descrption of all the available options using ``-h`` or ``--help`` options.

You can use densli to get results back from any of the `Server Density API <https://github.com/serverdensity/sd-api-docs>`_ endpoints, for example to access the `devices list <https://github.com/serverdensity/sd-api-docs/blob/master/sections/devices.md#list>`_::

    densli devices list

The above format "<section> <method>" can also be represented using a '/' or '.', e.g.:

 * ``devices.list``
 * ``devices/list``

Data to send to an endpoint can be defined as name-value pairs (seperated by an equals sign ``=``) using multiple ``-d`` or ``--data`` options, as piped in JSON, or as trailing name-value pair arguements, e.g. these are all the same::

    densli metrics getLatest -d deviceId=4e95d575160ba0212b003356
    densli metrics getLatest --data=deviceId=4e95d575160ba0212b003356
    densli metrics getLatest deviceId=4e95d575160ba0212b003356
    echo '{ "deviceId": "4e95d575160ba0212b003356" }' | densli metrics getLatest

densli is rather vocal about picking up settings and how it handles things (via ``STDOUT``), or about errors (via ``STDERR``), you might not want anything sent to ``STDOUT`` if you're piping densli's output to another process, to silence non-API output use the ``-q`` or ``-quiet`` options.

The default output for densli commands is human-readable JSON (indented with 4 spaces, regardless of the format that came back from the SD API), but for the `metrics getRange <https://github.com/serverdensity/sd-api-docs/blob/master/sections/metrics.md#get-range>`_ endpoint you can also get results outputted as a sparkline bargraphs (using the unicode characters 9601-9608) with the ``-s`` or ``--spark`` option, e.g.::

    densli metrics getRange -d deviceId=4e95d575160ba0212b003356 -d metric=diskUsage \
    -d rangeStart=012-08-25T00:00:00 -d rangeEnd=012-08-30T00:00:00 --spark

Will output something like::

    >>> /dev Used for 012-08-25T00:00:00 - 012-08-30T00:00:00:
    ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
    >>> /boot Used for 012-08-25T00:00:00 - 012-08-30T00:00:00:
    ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
    >>> / Used for 012-08-25T00:00:00 - 012-08-30T00:00:00:
    ▇▇▇▇▇▇▇▇▇▇▆▃▁▁▁▁▁▁▁▁
    >>> /var/lib/ureadahead/debugfs Used for 012-08-25T00:00:00 - 012-08-30T00:00:00:
    ▇▇▇▇▇▇▇▇▇▇▆▃▁▁▁▁▁▁▁▁

By default sparkline graphs are limited to a width of 20 characters for display purposes, but you can override this by setting the "max_graph_width" option to an integer of your choice in your ``config.json`` file.

To make sending postbacks to the `metrics.postback endpoint
<https://github.com/serverdensity/sd-api-docs/blob/master/sections/metrics.md#postback>`_ with piped in data more convenient you can use the ``-P`` or ``--postback`` option to flag ``STDIN`` data as a raw JSON payload which will be sent in a ``payload`` field as the postback endpoint expects, e.g.::

    echo '{ "agentKey": "blah", "someMetric": [...], "someOtherMetric": 1.0 }' \
    | densli metrics postback deviceId=4e95d575160ba0212b003356 --postback
