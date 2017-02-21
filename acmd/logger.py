# coding: utf-8
""" Logging module provides logging to stderr. We stick to the unix standard where only data
    is printed to stdout and process information is printed to stderr.

    Normal log messages are not displayed by default.
    warning and error log messages are always printed to stderr.
 """

import sys
import traceback

display_log = False


def init_log(_display_log):
    """ Initialize logging, if _display_log is true, debug logging will display on stderr """
    global display_log
    display_log = _display_log


def log(msg):
    """ Log debug messages if init_log was called with True """
    if display_log:
        sys.stderr.write("{}\n".format(msg))


def warning(msg):
    """ Warning messages are always printed to stderr """
    sys.stderr.write("warning: {}\n".format(msg))


def error(msg, e=None):
    """ Error message can be logged with exception info """
    sys.stderr.write("error: {}\n".format(msg))
    if e is not None:
        sys.stderr.write(traceback.format_exc())
