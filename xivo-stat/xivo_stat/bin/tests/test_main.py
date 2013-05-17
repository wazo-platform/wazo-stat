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
import sys
import unittest

from mock import Mock
from mock import patch
from xivo_stat.bin import stat


class TestMain(unittest.TestCase):

    @patch('xivo_stat.bin.stat._is_already_running', Mock(return_value=True))
    @patch('xivo.argparse_cmd.execute_command', Mock(side_effect=AssertionError('Should not be called')))
    def test_main_already_running(self):
        self.assertRaises(SystemExit, stat.main)

    @patch('xivo_stat.bin.stat._is_already_running', Mock(return_value=False))
    @patch('xivo_stat.bin.stat._add_pid_file', Mock())
    @patch('xivo.argparse_cmd.execute_command')
    def test_main_not_running(self, mock_execute_command):
        stat.main()

        self.assertEqual(mock_execute_command.call_count, 1)

    @patch('xivo_stat.bin.stat._is_already_running', Mock(return_value=False))
    @patch('xivo_stat.bin.stat._add_pid_file', Mock())
    @patch('xivo.argparse_cmd.execute_command', Mock(side_effect=lambda _: sys.exit(1)))
    @patch('xivo_stat.bin.stat._remove_pid_file')
    def test_pidfile_removed_on_error(self, mock_remove_pid_file):
        stat.main()

        self.assertEqual(mock_remove_pid_file.call_count, 1)

    @patch('os.unlink', Mock(side_effect=OSError(errno.ENOENT, 'msg')))
    def test_remove_pid_file_no_such_file_no_error(self):
        stat._remove_pid_file('/foo/bar')

    @patch('os.unlink', Mock(side_effect=OSError(errno.EACCES, 'msg')))
    def test_remove_pid_file_other_errno(self):
        self.assertRaises(OSError, stat._remove_pid_file, '/foo/bar')
