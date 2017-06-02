# coding: utf-8
""" Import StringIO module depending on python version. This variation allows
    python 2.7 to use non-unicode strings.
"""
try:
    import StringIO as stringio
except:
    import io as stringio


StringIO = stringio.StringIO


