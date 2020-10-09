# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import re

from datetime import datetime

from xivo import argparse_cmd
from xivo.daemonize import pidfile_context
from xivo.xivo_logging import setup_logging
from xivo_dao import init_db_from_config
from xivo_stat import core, config

PIDFILENAME = '/run/xivo-stat.pid'


def main():
    log_format = '%(asctime)s: %(message)s'
    main_config = config.get_config()
    init_db_from_config(main_config)
    setup_logging(
        main_config['log_filename'], debug=main_config['debug'], log_format=log_format
    )

    command = _XivoStatCommand(main_config)
    with pidfile_context(PIDFILENAME):
        argparse_cmd.execute_command(command)


class _XivoStatCommand(argparse_cmd.AbstractCommand):
    def __init__(self, main_config):
        self._config = main_config

    def configure_subcommands(self, subcommands):
        subcommands.add_subcommand(_FillDbSubcommand('fill_db', self._config))
        subcommands.add_subcommand(_CleanDbSubcommand('clean_db'))


class _FillDbSubcommand(argparse_cmd.AbstractSubcommand):
    _HELP_DATETIME_FORMAT = '%%Y-%%m-%%dT%%H:%%M:%%S'
    _DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, name, main_config):
        super(_FillDbSubcommand, self).__init__(name)
        self._config = main_config

    def configure_parser(self, parser):
        parser.add_argument(
            '--start',
            type=_datetime_iso,
            help='Start date to generate the statistics using this format: %s'
            % self._HELP_DATETIME_FORMAT,
        )
        parser.add_argument(
            '--end',
            type=_datetime_iso,
            default=datetime.now().strftime(self._DATETIME_FORMAT),
            help='End date to generate the statistics using this format: %s'
            % self._HELP_DATETIME_FORMAT,
        )

    def execute(self, parsed_args):
        core.update_db(
            config=self._config, start_date=parsed_args.start, end_date=parsed_args.end
        )


class _CleanDbSubcommand(argparse_cmd.AbstractSubcommand):
    def execute(self, _):
        core.clean_db()


def _datetime_iso(value):
    datetime_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
    datetime_pattern_re = re.compile(datetime_pattern)
    if not datetime_pattern_re.match(value):
        raise argparse.ArgumentTypeError('%s is not a valid datetime format' % value)
    return value
