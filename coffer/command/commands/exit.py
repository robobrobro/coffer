""" Functions and classes dealing with the exit command """

commands = ['exit']
description = 'Exits the program'

def execute(parsed_args=None, *args, **kwargs):
    """ Executes the exit command. """
    raise EOFError
