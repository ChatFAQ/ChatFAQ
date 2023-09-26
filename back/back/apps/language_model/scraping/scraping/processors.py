import re


def rm_dupl_ws(val):
    """Removes duplicate whitespaces"""
    return re.sub(' +', ' ', val)


def split(char):
    return lambda x: x.split(char)
