# coding: utf-8


def remove_prefix(prefix, text):
    if text.startswith(prefix):
        return text[len(prefix):]
    else:
        raise Exception("Expected {} to start with prefix {}".format(text, prefix))


def remove_suffix(suffix, text):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    else:
        raise Exception("Expected {} to end with prefix {}".format(text, suffix))
