# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import unittest
import datetime
from mock import patch
from xivo_stat import core
from xivo_stat.core import _ERASE_TIME_WHEN_STARTING


class TestCore(unittest.TestCase):
    def test_hour_start(self):
        t = datetime.datetime(2012, 1, 1, 1, 23, 37)

        expected = datetime.datetime(2012, 1, 1, 1, 0, 0)

        result = core.hour_start(t)

        self.assertEqual(result, expected)

    def test_end_of_previous_hour(self):
        t = datetime.datetime(2012, 1, 1, 1, 23, 37)

        expected = datetime.datetime(2012, 1, 1, 0, 59, 59, 999999)

        result = core.end_of_previous_hour(t)

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_queue_periodic_dao.get_most_recent_time')
    def test_get_start_time_has_call_on_queue_entry(self, mock_get_most_recent_time):
        mock_get_most_recent_time.return_value = datetime.datetime(2012, 1, 1, 1, 23, 54)

        expected = datetime.datetime(2012, 1, 1, 1, 0, 0) - _ERASE_TIME_WHEN_STARTING

        result = core.get_start_time()

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_queue_periodic_dao.get_most_recent_time')
    @patch('xivo_dao.queue_log_dao.get_first_time')
    def test_get_start_time_no_call_on_queue(self, mock_get_first_time, mock_get_most_recent_time):
        mock_get_most_recent_time.side_effect = LookupError('Empty table')
        mock_get_first_time.return_value = datetime.datetime(2012, 1, 1, 1, 12, 23, 666)

        expected = datetime.datetime(2012, 1, 1, 1, 0, 0) - _ERASE_TIME_WHEN_STARTING

        result = core.get_start_time()

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_queue_periodic_dao.get_most_recent_time')
    @patch('xivo_dao.queue_log_dao.get_first_time')
    def test_get_start_time_no_data(self, mock_get_first_time, mock_get_most_recent_time):
        mock_get_most_recent_time.side_effect = LookupError('Empty table')
        mock_get_first_time.side_effect = LookupError('Empty table')

        self.assertRaises(RuntimeError, core.get_start_time)

    def test_get_end_time(self):
        expected = datetime.datetime.now()

        result = core.get_end_time()

        self.assertTrue(result - expected < datetime.timedelta(seconds=1))

    @patch('xivo_stat.core.get_start_time')
    @patch('xivo_stat.core.get_end_time')
    def test_get_start_end_time(self, mock_end_time, mock_start_time):
        s = datetime.datetime(2012, 1, 1)
        e = datetime.datetime(2012, 1, 2)
        mock_start_time.return_value = s
        mock_end_time.return_value = e

        expected = s, e

        result = core.get_start_end_time()

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_agent_dao.clean_table')
    @patch('xivo_dao.stat_agent_periodic_dao.clean_table')
    @patch('xivo_dao.stat_call_on_queue_dao.clean_table')
    @patch('xivo_dao.stat_queue_dao.clean_table')
    @patch('xivo_dao.stat_queue_periodic_dao.clean_table')
    def test_clean_db(self, mock_clean_table_stat_queue_periodic,
                      mock_clean_table_queue_dao,
                      mock_clean_table_stat_call_on_queue,
                      mock_clean_table_stat_agent_periodic,
                      mock_clean_table_stat_agent_dao):
        core.clean_db()

        mock_clean_table_stat_agent_dao.assert_called_once_with()
        mock_clean_table_stat_agent_periodic.assert_called_once_with()
        mock_clean_table_stat_call_on_queue.assert_called_once_with()
        mock_clean_table_queue_dao.assert_called_once_with()
        mock_clean_table_stat_queue_periodic.assert_called_once_with()

    @patch('xivo_dao.queue_log_dao.get_queue_names_in_range')
    @patch('xivo_dao.stat_queue_dao.insert_if_missing')
    def test_insert_missing_queues(self, mock_insert_if_missing, mock_get_queue_names_in_range):
        start = datetime.datetime(2012, 1, 1, 1, 1, 1)
        end = datetime.datetime(2012, 1, 2, 1, 1, 1)
        queue_names = ['queue_%s' % x for x in range(10)]
        mock_get_queue_names_in_range.return_value = queue_names

        core.insert_missing_queues(start, end)

        mock_insert_if_missing.assert_called_once_with(queue_names)

    @patch('xivo_dao.stat_agent_dao.insert_missing_agents')
    def test_insert_missing_agents(self, mock_insert_agent_if_missing):
        core.insert_missing_agents()

        mock_insert_agent_if_missing.assert_called_once_with()
