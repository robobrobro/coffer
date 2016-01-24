""" 
Helper functions for main entry point
"""

from .version import __version__
import argparse
import sys

def parse_args(*args, **kwargs):
    parser = argparse.ArgumentParser(prog='coffer', description='[(en)|(de)]crypts files')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s {}'.format(__version__))
    return vars(parser.parse_args())

def main(argv=None, *args, **kwargs):
    """
    Main entry point

    Parameters:
        argv    list of string arguments composing a command line
    """

    if argv is None:
        argv = sys.argv
    parsed_dict = parse_args(argv)
