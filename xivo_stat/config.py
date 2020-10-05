# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy

_DEFAULT_CONFIG = {
    'config_file': '/etc/wazo-stat/config.yml',
    'extra_config_files': '/etc/wazo-stat/conf.d',
    'log_filename': '/var/log/xivo-stat.log',
    'debug': False,
    'db_uri': 'postgresql://asterisk:proformatique@localhost/asterisk?application_name=wazo-stat',
}


def get_config():
    file_config = read_config_file_hierarchy(_DEFAULT_CONFIG)
    return ChainMap(file_config, _DEFAULT_CONFIG)
