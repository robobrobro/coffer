#!/usr/bin/env python

from coffer import get_program_name, get_description, __version__
from distutils.core import setup

setup(
    name = 'coffer',
    version = __version__,
    description = get_description,
    author = 'L.J. Hill',
    author_email = 'larry.hill3@gmail.com',
    url = 'https://github.com/robobrobro/coffer',
    packages = ['coffer'],
    package_data = {
        'coffer': [
            'command/*',
            'command/commands/*',
        ],
    },
    entry_points = {
        'console_scripts': [
            'coffer = coffer.__main__:main',
        ],
    },
)
