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
