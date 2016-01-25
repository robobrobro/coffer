""" Functions dealing with parsing commands. """

from pkgutil import walk_packages

from . import commands
from .execute import execute_module_command
from .invalid import print_invalid_command

def parse_command_line(command_line=[], *args, **kwargs):
    """
    Parses the given command line and returns a command object if the syntax is valid.
    Otherwise, the function returns None.

    command_line        list of strings to be parsed as a command line
    interactive         whether the program is running in interactive mode
    """

    interactive = kwargs.get('interactive', False)

    if len(command_line) > 0:
        command = command_line[0]

        # If running in interactive mode and the command starts with a dash,
        # print invalid command instead of passing it to the help command
        # to avoid possibly conflicting with help's options
        if interactive and command.startswith('-'):
            print_invalid_command(command)
            return False

        # Recursively search through modules in commands for the first command
        # that matches the command name in the command line
        for loader, name, ispkg in walk_packages(commands.__path__):
            module = loader.find_module(name).load_module(name)
            ret = execute_module_command(module, command=command, command_line=command_line[1:],
                    *args, **kwargs)
            if ret is not None:
                return ret

        print_invalid_command(command)
        return False
