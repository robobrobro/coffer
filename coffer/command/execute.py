""" Functions dealing with execute commands. """

import argparse

def execute_module_command(module, command='', command_line=[], *args, **kwargs):
    """
    Executes the given command line in the given module.

    module              the module command to execute
    command_line        list of strings to be parsed as a command line
    interactive         whether the program is running in interactive mode
    """

    module_commands = getattr(module, 'commands', [])
    module_description = getattr(module, 'description', '')
    module_arguments = getattr(module, 'arguments', [])
    module_execute = getattr(module, 'execute', None)
    interactive = kwargs.get('interactive', False)

    # If running in interactive mode, ignore the dashed commands (e.g. -h)
    if interactive:
        module_commands = list(filter(lambda c: not c.startswith('-'), module_commands))

    # If the command can be handled by the module, parse the command line
    # and execute the command in the context of the parsed arguments.
    if module_execute and command in module_commands:
        parser = argparse.ArgumentParser(prog=module_commands[0], description=module_description)
        for arg in module_arguments:
            parser.add_argument(*arg[0], **arg[1])
        parsed_args = parser.parse_args(command_line)
        return module_execute(parsed_args=parsed_args, *args, **kwargs)
    
    return None
