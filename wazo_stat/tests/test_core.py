# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import unittest
from unittest.mock import ANY, patch, sentinel

from wazo_stat import core
from wazo_stat.core import _ERASE_TIME_WHEN_STARTING


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
        mock_get_most_recent_time.return_value = datetime.datetime(
            2012, 1, 1, 1, 23, 54
        )

        expected = datetime.datetime(2012, 1, 1, 1, 0, 0) - _ERASE_TIME_WHEN_STARTING

        result = core.get_start_time(sentinel.dao_sess)

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_queue_periodic_dao.get_most_recent_time')
    @patch('xivo_dao.queue_log_dao.get_first_time')
    def test_get_start_time_no_call_on_queue(
        self, mock_get_first_time, mock_get_most_recent_time
    ):
        mock_get_most_recent_time.side_effect = LookupError('Empty table')
        mock_get_first_time.return_value = datetime.datetime(2012, 1, 1, 1, 12, 23, 666)

        expected = datetime.datetime(2012, 1, 1, 1, 0, 0) - _ERASE_TIME_WHEN_STARTING

        result = core.get_start_time(sentinel.dao_sess)

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_queue_periodic_dao.get_most_recent_time')
    @patch('xivo_dao.queue_log_dao.get_first_time')
    def test_get_start_time_no_data(
        self, mock_get_first_time, mock_get_most_recent_time
    ):
        mock_get_most_recent_time.side_effect = LookupError('Empty table')
        mock_get_first_time.side_effect = LookupError('Empty table')

        self.assertRaises(RuntimeError, core.get_start_time, sentinel.dao_sess)

    @patch('xivo_dao.stat_agent_dao.clean_table')
    @patch('xivo_dao.stat_agent_periodic_dao.clean_table')
    @patch('xivo_dao.stat_call_on_queue_dao.clean_table')
    @patch('xivo_dao.stat_queue_dao.clean_table')
    @patch('xivo_dao.stat_queue_periodic_dao.clean_table')
    def test_clean_db(
        self,
        mock_clean_table_stat_queue_periodic,
        mock_clean_table_queue_dao,
        mock_clean_table_stat_call_on_queue,
        mock_clean_table_stat_agent_periodic,
        mock_clean_table_stat_agent_dao,
    ):
        core.clean_db()

        mock_clean_table_stat_agent_dao.assert_called_once_with(ANY)
        mock_clean_table_stat_agent_periodic.assert_called_once_with(ANY)
        mock_clean_table_stat_call_on_queue.assert_called_once_with(ANY)
        mock_clean_table_queue_dao.assert_called_once_with(ANY)
        mock_clean_table_stat_queue_periodic.assert_called_once_with(ANY)

    @patch('xivo_dao.queue_log_dao.get_queue_names_in_range')
    @patch('xivo_dao.stat_queue_dao.insert_if_missing')
    def test_insert_missing_queues(
        self, mock_insert_if_missing, mock_get_queue_names_in_range
    ):
        start = datetime.datetime(2012, 1, 1, 1, 1, 1)
        end = datetime.datetime(2012, 1, 2, 1, 1, 1)
        queue_names = ['queue_%s' % x for x in range(10)]
        mock_get_queue_names_in_range.return_value = queue_names

        core.insert_missing_queues(
            sentinel.dao_sess,
            start,
            end,
            sentinel.confd_queues,
            sentinel.master_tenant,
        )

        mock_insert_if_missing.assert_called_once_with(
            sentinel.dao_sess,
            queue_names,
            sentinel.confd_queues,
            sentinel.master_tenant,
        )

    @patch('xivo_dao.stat_agent_dao.insert_missing_agents')
    def test_insert_missing_agents(self, mock_insert_agent_if_missing):
        core.insert_missing_agents(sentinel.dao_sess, sentinel.confd_agents)

        mock_insert_agent_if_missing.assert_called_once_with(
            sentinel.dao_sess, sentinel.confd_agents
        )
