from coffer import config
from ConfigParser import SafeConfigParser
import mock
import os
import tempfile

def expand_string(s, *args, **kwargs):
    return os.path.expanduser(os.path.expandvars(s))

def assert_config_equals(cfg, d, *args, **kwargs):
    cfg_dict = {}
    for section in cfg.sections():
        for option in cfg.options(section):
            if not cfg_dict.has_key(section):
                cfg_dict[section] = {}
            cfg_dict[section][option] = cfg.get(section, option)

    for k, v in d.iteritems():
        k = k.lower()
        assert cfg_dict.has_key(k)
        if isinstance(v, dict):
            for kk, vv in v.iteritems():
                kk = kk.lower()
                assert isinstance(cfg_dict[k], dict)
                assert cfg_dict[k].has_key(kk)
                assert expand_string(cfg_dict[k][kk]) == expand_string(vv)
        else:
            assert expand_string(d[k]) == expand_string(v)

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

def test_load_default_config(*args, **kwargs):
    with tempfile.NamedTemporaryFile() as tmpfile:
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
            assert_config_equals(cfg, config._defaults)

def test_load_custom_config(*args, **kwargs):
    with tempfile.NamedTemporaryFile() as tmpfile:
        tmpfile.write('[interactive]\nprompt = test>\n')
        custom_cfg_dict = {'interactive': {'prompt': 'test>'}}
        custom_cfg_dict.update(config._defaults)
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
            assert_config_equals(cfg, custom_cfg_dict)

