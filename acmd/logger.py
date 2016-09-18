# coding: utf-8
import sys
import traceback

display_log = False

out = sys.stderr


def init_log(_display_log):
    global display_log
    display_log = _display_log


def log(msg):
    global display_log
    if display_log:
        out.write("{}\n".format(msg))


def warning(msg):
    out.write("warning: {}\n".format(msg))


def error(msg, e=None):
    sys.stderr.write("error: {}\n".format(msg))
    if e is not None:
        out.write(traceback.format_exc())
