from coffer import config
from nose.tools import *
import mock
import os
import stat
import tempfile

import sys
if sys.version_info[0] < 3:
    from ConfigParser import SafeConfigParser
else:
    from configparser import SafeConfigParser
    basestring = str

class LoggerDecoy(object):
    def error(self, *args, **kwargs):
        pass

def expand_string(s, *args, **kwargs):
    return os.path.expanduser(os.path.expandvars(s))

def assert_config_equals(cfg, d, *args, **kwargs):
    cfg_dict = {}
    for section in cfg.sections():
        for option in cfg.options(section):
            if not section in cfg_dict:
                cfg_dict[section] = {}
            cfg_dict[section][option] = cfg.get(section, option)

    for k, v in d.items():
        k = k.lower()
        ok_(k in cfg_dict, '{} not in {}'.format(k, cfg_dict))
        if isinstance(v, dict):
            for kk, vv in v.items():
                kk = kk.lower()
                ok_(isinstance(cfg_dict[k], dict), '{} is not a dict'.format(cfg_dict[k]))
                ok_(kk in cfg_dict[k], '{} not in {}'.format(kk, cfg_dict[k]))
                eq_(expand_string(cfg_dict[k][kk]), expand_string(vv))
        else:
            eq_(expand_string(d[k]), expand_string(v))

def test_ensure_defaults(*args, **kwargs):
    cfg = SafeConfigParser()
    config._ensure_defaults(cfg)
    assert_config_equals(cfg, config._defaults)

def test_ensure_defaults_twice(*args, **kwargs):
    cfg = SafeConfigParser()
    config._ensure_defaults(cfg)
    assert_config_equals(cfg, config._defaults)
    config._ensure_defaults(cfg)
    assert_config_equals(cfg, config._defaults)

def test_config_fixup_double_quotation_mark_only(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', '"')
    config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), '')

def test_config_fixup_beginning_double_quotation_mark(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', '"test')
    config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), 'test')

def test_config_fixup_ending_double_quotation_mark(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', 'test"')
    config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), 'test')

def test_config_fixup_wrapped_double_quotation_marks(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', '"test"')
    config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), 'test')

def test_config_fixup_single_quotation_mark_only(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', '\'')
    config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), '')

def test_config_fixup_beginning_single_quotation_mark(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', '\'test')
    config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), 'test')

def test_config_fixup_ending_single_quotation_mark(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', 'test\'')
    config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), 'test')

def test_config_fixup_wrapped_single_quotation_marks(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', '\'test\'')
    config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), 'test')

def test_config_fixup_expand_environment_var(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', '$TEST')
    environ = {'TEST': 'success'}
    with mock.patch('os.environ', environ):
        config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), 'success')

def test_config_fixup_expand_user_var(*args, **kwargs):
    cfg = SafeConfigParser()
    cfg.add_section('test')
    cfg.set('test', 'test', '~')
    environ = {'HOME': 'success'}
    with mock.patch('os.environ', environ):
        config._config_fixup(cfg)
    eq_(cfg.get('test', 'test'), 'success')

def test_load_default_config(*args, **kwargs):
    with tempfile.NamedTemporaryFile() as tmpfile:
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
        assert_config_equals(cfg, config._defaults)

def test_load_custom_config(*args, **kwargs):
    with tempfile.NamedTemporaryFile() as tmpfile:
        tmpfile.write(b'[interactive]\nprompt = test>\n')
        custom_cfg_dict = {'interactive': {'prompt': 'test>'}}
        custom_cfg_dict.update(config._defaults)
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
        assert_config_equals(cfg, custom_cfg_dict)

def test_save_config_with_modifications(*args, **kwargs):
    with tempfile.NamedTemporaryFile() as tmpfile:
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
    assert_config_equals(cfg, config._defaults)

    cfg.add_section('test')
    cfg.set('test', 'test', 'test')

    with tempfile.NamedTemporaryFile() as tmpfile:
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            config.save_config(cfg)
            loaded_cfg = config.load_config()

    new_dict = {'test': {'test': 'test'}}
    new_dict.update(config._defaults)
    assert_config_equals(loaded_cfg, new_dict)

def test_save_config_to_readonly_file_no_logger(*args, **kwargs):
    with tempfile.NamedTemporaryFile() as tmpfile:
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
    assert_config_equals(cfg, config._defaults)

    cfg.add_section('test')
    cfg.set('test', 'test', 'test')

    with tempfile.NamedTemporaryFile() as tmpfile:
        os.chmod(tmpfile.name, ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            config.save_config(cfg)
            loaded_cfg = config.load_config()
    assert_config_equals(loaded_cfg, config._defaults)

def test_save_config_to_readonly_file_with_logger(*args, **kwargs):
    with tempfile.NamedTemporaryFile() as tmpfile:
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
    assert_config_equals(cfg, config._defaults)

    cfg.add_section('test')
    cfg.set('test', 'test', 'test')

    with tempfile.NamedTemporaryFile() as tmpfile:
        os.chmod(tmpfile.name, ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            config.save_config(cfg, logger=LoggerDecoy())
            loaded_cfg = config.load_config()
    assert_config_equals(loaded_cfg, config._defaults)

def test_save_config_to_non_existent_file(*args, **kwargs):
    with tempfile.NamedTemporaryFile() as tmpfile:
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
    assert_config_equals(cfg, config._defaults)

    cfg.add_section('test')
    cfg.set('test', 'test', 'test')

    with tempfile.NamedTemporaryFile() as tmpfile:
        filename = tmpfile.name
    ok_(not os.path.exists(filename), '{} exists'.format(filename))

    environ = {'COFFER_CONFIG': filename}
    with mock.patch('os.environ', environ):
        config.save_config(cfg)
        loaded_cfg = config.load_config()
    assert_config_equals(loaded_cfg, config._defaults)

