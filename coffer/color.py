""" Functions and classes dealing with coloring text """

import os
import sys

def colorize(code, text, *args, **kwargs):
    """
    If running in a tty console, text is wrapped with the given ANSI color code.
    Otherwise, text is returned unchanged.
    """

    if os.isatty(1):
        return '\[\e[{code}m\]{text}\[\e[0m\]'.format(code=code, text=text)
    else:
        return text
