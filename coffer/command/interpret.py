""" Functions dealing with interpreting commands via a CLI. """

from pkgutil import walk_packages
import atexit
import glob
import os
import re
import readline
import shlex
import sys

from . import commands as commands_pkg
from .parse import parse_command_line

def _get_input(cfg=None, logger=None, *args, **kwargs):
    if not cfg: return ''

    prompt = cfg.get('interactive', 'prompt')
    if sys.version_info[0] < 3:
        command_line = raw_input(prompt)
    else:
        command_line = input(prompt)

    try:
        return shlex.split(command_line)
    except ValueError as e:
        print('Syntax error: {err}'.format(err=e))

    return []

def _setup_readline(cfg=None, logger=None, *args, **kwargs):
    if not cfg: return False

    # Setup tab completion
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims(' \t\n;')
    completer = Completer(logger=logger)
    readline.set_completer(completer.complete)

    # Setup command-line history
    max_history_length = cfg.get('interactive', 'max_history_length')
    readline.set_history_length(int(max_history_length, 0))
    history_filename = cfg.get('interactive', 'history_file')
    if os.path.exists(history_filename):
        readline.read_history_file(history_filename)

    # Register shutdown function
    atexit.register(_teardown_readline, history_filename)

    return True

def _teardown_readline(history_filename):
    # Save command line history
    try:
        readline.write_history_file(history_filename)
    except (IOError, OSError):
        pass

class Completer(object):
    def __init__(self, *args, **kwargs):
        logger = kwargs.get('logger', None)

        # Recursively search through modules in commands package to scrape command names
        self.commands = []
        for loader, name, ispkg in walk_packages(commands_pkg.__path__):
            try:
                module = loader.find_module(name).load_module(name)
                module_commands = getattr(module, 'commands', [])
                if len(module_commands) > 0:
                    self.commands.append(module_commands[0])
            except ImportError as e:
                if logger: logger.error('Failed to import {name} module: {err}'.format(name=name, err=e))

    def __complete_path(self, path):
        if not path:
            path = ''
        else:
            path = path.strip()
        return glob.glob(path + '.*') + glob.glob(path + '*')

    def complete(self, text, state):
        buf = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        if not line:
            return [command + ' ' for command in self.commands][state]

        # TODO necessary?
        if re.match(r'.*\s+$', buf, re.M):
            line.append('')

        if len(line) > 1:
            results = self.__complete_path(line[-1]) + [None]
            return results[state]
        else:
            command = line[0].strip()

            # TODO call command module's complete
            #if command in self.commands:

            results = [cmd for cmd in self.commands if cmd.startswith(command)] + [None]
            return results[state]

def interpret_command_line(cfg=None, logger=None, *args, **kwargs):
    if not _setup_readline(cfg=cfg, logger=logger):
        return False

    # Interpret command lines
    try:
        while True:
            command_line = _get_input(cfg=cfg, logger=logger)
            try:
                parse_command_line(command_line, cfg=cfg, logger=logger, *args, **kwargs)
            except SystemExit:
                pass
    except (EOFError, KeyboardInterrupt):
        pass
