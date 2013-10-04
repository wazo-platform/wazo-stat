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

import sys
import unittest

from mock import Mock
from mock import patch
from xivo_stat.bin import stat


class TestMain(unittest.TestCase):

    @patch('xivo.pid_file.is_already_running', Mock(return_value=True))
    @patch('xivo.argparse_cmd.execute_command', Mock(side_effect=AssertionError('Should not be called')))
    def test_main_already_running(self):
        self.assertRaises(SystemExit, stat.main)

    @patch('xivo.pid_file.is_already_running', Mock(return_value=False))
    @patch('xivo.pid_file.add_pid_file', Mock())
    @patch('xivo.argparse_cmd.execute_command')
    def test_main_not_running(self, mock_execute_command):
        stat.main()

        self.assertEqual(mock_execute_command.call_count, 1)

    @patch('xivo.pid_file.is_already_running', Mock(return_value=False))
    @patch('xivo.pid_file.add_pid_file', Mock())
    @patch('xivo.argparse_cmd.execute_command', Mock(side_effect=lambda _: sys.exit(1)))
    @patch('xivo.pid_file.remove_pid_file')
    def test_pidfile_removed_on_error(self, mock_remove_pid_file):
        stat.main()

        self.assertEqual(mock_remove_pid_file.call_count, 1)
