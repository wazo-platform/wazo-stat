# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013  Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import errno
import logging
import os
import sys

from contextlib import contextmanager
from xivo import argparse_cmd
from xivo_stat import core

PIDFILENAME = '/var/run/xivo-stat.pid'


@contextmanager
def pidfile(filename):
    try:
        yield _add_pid_file(filename)
    except SystemExit:
        pass  # The pidfile should be closed on sys.exit()
    finally:
        _remove_pid_file(filename)


def main():
    if _is_already_running(PIDFILENAME):
        print 'XiVO stat is already running'
        sys.exit(1)

    command = _XivoStatCommand()
    with pidfile(PIDFILENAME):
        argparse_cmd.execute_command(command)


def _is_already_running(filename):
    return os.path.isfile(filename)


def _add_pid_file(filename):
    with open(filename, 'w') as f:
        f.write(str(os.getpid()))


def _remove_pid_file(filename):
    try:
        os.unlink(filename)
    except OSError, e:
        if e.errno != errno.ENOENT:
            raise


class _XivoStatCommand(argparse_cmd.AbstractCommand):

    def pre_execute(self, _):
        self._init_logging()

    def _init_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        root_logger.addHandler(handler)

    def configure_subcommands(self, subcommands):
        subcommands.add_subcommand(_FillDbSubcommand('fill_db'))
        subcommands.add_subcommand(_CleanDbSubcommand('clean_db'))


class _FillDbSubcommand(argparse_cmd.AbstractSubcommand):

    def execute(self, _):
        core.update_db()


class _CleanDbSubcommand(argparse_cmd.AbstractSubcommand):

    def execute(self, _):
        core.clean_db()
