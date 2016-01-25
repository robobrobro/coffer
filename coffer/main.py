"""
Helper functions for main entry point
"""

from .command.interpret import interpret_command_line
from .config import load_config
from .version import __version__
import argparse
import sys

__prog__ = 'coffer'
__description__ = '[(en)|(de)]crypts files'

def get_program_name(*args, **kwargs):
    """ Gets program's name """
    return __prog__

def get_description(*args, **kwargs):
    """ Gets program's description """
    return __description__

def parse_args(*args, **kwargs):
    parser = argparse.ArgumentParser(prog=__prog__, description=__description__)
    parser.add_argument('-V', '--version', action='version', version='%(prog)s {}'.format(__version__))
    return vars(parser.parse_args())

def main(argv=None, *args, **kwargs):
    """
    Main entry point

    Parameters:
        argv    list of string arguments composing a command line
    """

    # Parse command-line arguments
    if argv is None:
        argv = sys.argv
    parsed_dict = parse_args(argv)

    # Load configuration file
    cfg = load_config()

    # Run interactive command-line console
    interpret_command_line(cfg, interactive=True)
