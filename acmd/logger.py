# coding: utf-8
import sys

display_log = False

def init_log(_display_log):
    global display_log
    display_log = _display_log


def log(msg):
    if display_log:
        sys.stderr.write("{}\n".format(msg))


def warn(msg):
    sys.stderr.write("warning: {}\n".format(msg))


def error(msg, exit_code=-1):
    sys.stderr.write("error: {}\n".format(msg))
    sys.exit(exit_code)
