from coffer import config
import mock
import os
import tempfile
import sys
if sys.version_info[0] < 3:
    from ConfigParser import SafeConfigParser
else:
    from configparser import SafeConfigParser
    basestring = str

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
        assert k in cfg_dict
        if isinstance(v, dict):
            for kk, vv in v.items():
                kk = kk.lower()
                assert isinstance(cfg_dict[k], dict)
                assert kk in cfg_dict[k]
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
        tmpfile.write(b'[interactive]\nprompt = test>\n')
        custom_cfg_dict = {'interactive': {'prompt': 'test>'}}
        custom_cfg_dict.update(config._defaults)
        environ = {'COFFER_CONFIG': tmpfile.name}
        with mock.patch('os.environ', environ):
            cfg = config.load_config()
            assert_config_equals(cfg, custom_cfg_dict)

