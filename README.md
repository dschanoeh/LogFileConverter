LogFileConverter
================

LogFileConverter is a simple python script that can convert SocketCAN log files (.log or gzipped as .log.gz)
to the strict log file syntax that Kayak uses. This syntax is still fully compatible to the SocketCAN syntax.

Conversion
----------

The LogFileConverter does:

* separate content from header (all header lines first)
* concentrate multiline descriptions to a single line
* add device aliases for busses that are not listed yet
* add empty descriptions if not present
* ignore malformed lines

Example
-------

This log file (ugly.log):

    (0.000000) can2 5D1#000000
    DEVICE_ALIAS Powertrain can0
    DEVICE_ALIAS Comfort can1
    DESCRIPTION "this is a simple
    PLATFORM FOO
    (0.100000) can1 001#0000
    DESCRIPTION multiline
    DESCRIPTION description"

    malformedline

will be transformed to:

    DESCRIPTION "this is a simple multiline description"
    PLATFORM FOO
    DEVICE_ALIAS can2 can2
    DEVICE_ALIAS Powertrain can0
    DEVICE_ALIAS Comfort can1
    (0.000000) can2 5D1#000000
    (0.100000) can1 001#0000

by

    ./LogFileConverter.py ugly.log


