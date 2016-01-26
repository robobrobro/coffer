""" Functions and classes dealing with the configuration file """

import sys
if sys.version_info[0] < 3:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser
    basestring = str
import os
import re

from . import color

_defaults = {
        'interactive': {
            'PROMPT': '[coffer]? ',
            'HISTORY_FILE': '~/.coffer_history',
            'MAX_HISTORY_LENGTH': '2000',
        },
}

def _ensure_defaults(cfg, *args, **kwargs):
    for section, optdata in _defaults.items():
        if not cfg.has_section(section):
            cfg.add_section(section)
        for option, value in optdata.items():
            if not cfg.has_option(section, option):
                cfg.set(section, option, value)

def _config_fixup(cfg, *args, **kwargs):
    for section in cfg.sections():
        for option in cfg.options(section):
            # Remove leading and trailing quotations marks
            cfg.set(section, option, cfg.get(section, option).lstrip('"\'').rstrip('"\''))
            # Expand user and environment variables
            cfg.set(section, option, os.path.expanduser(os.path.expandvars(cfg.get(section, option))))
            # Fix ANSI color escape sequences
            value = re.sub(r'\\(e|033|[Xx]1[Bb])', '\x1b', cfg.get(section, option))
            value = re.sub(r'\\(\[|001|[Xx]01)', '\x01', value)
            value = re.sub(r'\\(\]|002|[Xx]02)', '\x02', value)
            cfg.set(section, option, value)

def load_config(*args, **kwargs):
    cfg = ConfigParser()

    filename = os.path.expanduser(os.path.expandvars((os.environ.get('COFFER_CONFIG', '~/.cofferrc'))))
    cfg.read(filename)

    # Ensure defaults exist
    _ensure_defaults(cfg)

    # Post-processing
    _config_fixup(cfg)

    return cfg

def save_config(cfg, *args, **kwargs):
    try:
        with open(FILENAME, 'w') as f:
            cfg.write(f)
    except (IOError, OSError) as e:
        logger = kwargs.get('logger', None)
        if logger:
            logger.error('{filename}: {err}'.format(filename=e.filename, err=e.strerror))
        return False
    return True

def get_option(cfg, section, option, default=None, option_type='', *args, **kwargs):
    if not cfg.has_section(section): return default
    if not cfg.has_option(section, option): return default

    getfunc = getattr(cfg, 'get{type}'.format(type=option_type), None)
    if not callable(getfunc): return default

    return getfunc(section, option)

def get_option_bool(*args, **kwargs):
    kwargs['option_type'] = 'bool'
    return get_option(*args, **kwargs)

def get_option_float(*args, **kwargs):
    kwargs['option_type'] = 'float'
    return get_option(*args, **kwargs)

def get_option_int(*args, **kwargs):
    kwargs['option_type'] = 'int'
    return get_option(*args, **kwargs)

def get_option_list(*args, **kwargs):
    kwargs['option_type'] = ''
    value = get_option(*args, **kwargs)
    if not isinstance(value, basestring): return value
    return [s.strip('"\' \t') for s in value.split(',')]

def set_option(cfg, section, option, value, *args, **kwargs):
    if not cfg: return False

    if not cfg.has_section(section):
        cfg.add_section(section)

    #if not cfg.has_option(section, option):
    #    cfg.add_option(section, option)

    cfg.set(section, option, str(value))
    return True

def set_option_list(cfg, section, option, value, *args, **kwargs):
    return set_option(cfg, section, option, ','.join(value), *args, **kwargs)
