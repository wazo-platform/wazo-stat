# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy, parse_config_file

_DEFAULT_CONFIG = {
    'config_file': '/etc/wazo-stat/config.yml',
    'extra_config_files': '/etc/wazo-stat/conf.d',
    'log_filename': '/var/log/wazo-stat.log',
    'debug': False,
    'db_uri': 'postgresql://asterisk:proformatique@localhost/asterisk?application_name=wazo-stat',
    'confd': {'host': 'localhost', 'port': 9486, 'prefix': None, 'https': False},
    'auth': {
        'host': 'localhost',
        'port': 9497,
        'prefix': None,
        'https': False,
        'key_file': '/var/lib/wazo-auth-keys/wazo-stat-key.yml',
    },
}


def _load_key_file(config):
    key_file = parse_config_file(config['auth']['key_file'])
    if not key_file:
        return {}
    return {
        'auth': {
            'username': key_file['service_id'],
            'password': key_file['service_key'],
        }
    }


def get_config():
    file_config = read_config_file_hierarchy(_DEFAULT_CONFIG)
    service_key = _load_key_file(ChainMap(file_config, _DEFAULT_CONFIG))
    return ChainMap(service_key, file_config, _DEFAULT_CONFIG)
