""" Functions and classes dealing with the help command """

import argparse
from pkgutil import walk_packages

from coffer import get_description, get_program_name
from coffer.command import commands as coffer_commands
from coffer.command.execute import execute_module_command
from coffer.command.invalid import print_invalid_command

commands = ['help', '-h', '--help']
description = 'Prints a list of available commands or help on a specific command'
arguments = [
        (('command',), {'nargs': '?', 'help': 'command for which help is desired'}),
]

def execute(parsed_args=None, interactive=False, *args, **kwargs):
    """ Executes the help command. """

    if not parsed_args or not parsed_args.command:
        if not interactive:
            usage = '%(prog)s [command line]'
            description = get_description()
            group_title = 'commands'
        else:
            usage = argparse.SUPPRESS
            description = None
            group_title = None

        parser = argparse.ArgumentParser(prog=get_program_name(), description=description,
                usage=usage, add_help=False)

        # Recursively search through foe command modules and
        # add an argument to the parser for each command.
        group = parser.add_argument_group(title=group_title)
        for loader, name, ispkg in walk_packages(coffer_commands.__path__):
            module = loader.find_module(name).load_module(name)
            module_commands = getattr(module, 'commands', [])
            module_description = getattr(module, 'description', '')
            non_dash_commands = list(filter(lambda c: not c.startswith('-'), module_commands))
            if non_dash_commands:
                group.add_argument(*non_dash_commands, help=module_description)
            dash_commands = list(filter(lambda c: c.startswith('-'), module_commands))
            if dash_commands and not interactive:
                group.add_argument(*dash_commands, help=module_description, action='store_true')

        parser.print_help()
        return True
    else:
        # Recursively search through foe command modules.
        for loader, name, ispkg in walk_packages(coffer_commands.__path__):
            module = loader.find_module(name).load_module(name)
            module_commands = getattr(module, 'commands', [])

            # If the command can be handled by the module,
            # and execute the command's help function.
            if parsed_args.command in module_commands:
                return execute_module_command(module, command=parsed_args.command, command_line=['-h'])

        print_invalid_command(parsed_args.command)
        return False
