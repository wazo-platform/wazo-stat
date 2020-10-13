# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import re

from datetime import datetime

from xivo.daemonize import pidfile_context
from xivo.xivo_logging import setup_logging
from xivo_dao import init_db_from_config
from wazo_stat import core, config

PIDFILENAME = '/run/wazo-stat.pid'
HELP_DATETIME_FORMAT = '%%Y-%%m-%%dT%%H:%%M:%%S'


def main():
    log_format = '%(asctime)s: %(message)s'
    main_config = config.get_config()
    init_db_from_config(main_config)
    setup_logging(
        main_config['log_filename'], debug=main_config['debug'], log_format=log_format
    )

    with pidfile_context(PIDFILENAME):
        parser = argparse.ArgumentParser(description='Wazo statistics generator')
        options = parse_args(parser)
        subcommand = getattr(options, 'subcommand', None)

        if subcommand == 'fill_db':
            core.update_db(
                config=main_config,
                start_date=options.start,
                end_date=options.end,
            )
        elif subcommand == 'clean_db':
            core.clean_db()
        else:
            parser.print_help()


def parse_args(parser):
    subparsers = parser.add_subparsers()
    fill_db_parser = subparsers.add_parser('fill_db')
    fill_db_parser.set_defaults(subcommand='fill_db')
    clean_db_parser = subparsers.add_parser('clean_db')
    clean_db_parser.set_defaults(subcommand='clean_db')

    fill_db_parser.add_argument(
        '--start',
        type=_datetime_iso,
        help='Start date to generate the statistics using this format: {}'.format(
            HELP_DATETIME_FORMAT
        ),
    )
    fill_db_parser.add_argument(
        '--end',
        type=_datetime_iso,
        default=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        help='End date to generate the statistics using this format: {}'.format(
            HELP_DATETIME_FORMAT
        )
    )

    return parser.parse_args()


def _datetime_iso(value):
    datetime_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
    datetime_pattern_re = re.compile(datetime_pattern)
    if not datetime_pattern_re.match(value):
        raise argparse.ArgumentTypeError('%s is not a valid datetime format' % value)
    return value
