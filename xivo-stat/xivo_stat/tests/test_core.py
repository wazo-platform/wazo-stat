# -*- coding: utf-8 -*-
import unittest
import datetime
from mock import Mock
from mock import patch
from xivo_stat import core

mock_end_time = Mock()
mock_fill_calls = Mock()
mock_get_agents_after = Mock()
mock_get_first_time = Mock()
mock_get_most_recent_time = Mock()
mock_get_queue_names_in_range = Mock()
mock_insert_agent_if_missing = Mock()
mock_insert_if_missing = Mock()
mock_insert_missing_agents = Mock()
mock_insert_missing_queues = Mock()
mock_insert_periodic_stat = Mock()
mock_start_time = Mock()
mock_clean_table_stat_call_on_queue = Mock()
mock_clean_table_stat_queue_periodic = Mock()

mocks = [mock_end_time,
         mock_fill_calls,
         mock_get_agents_after,
         mock_get_first_time,
         mock_get_most_recent_time,
         mock_insert_agent_if_missing,
         mock_insert_if_missing,
         mock_insert_missing_agents,
         mock_insert_missing_queues,
         mock_insert_periodic_stat,
         mock_start_time,
         mock_clean_table_stat_call_on_queue,
         mock_clean_table_stat_queue_periodic]


class TestCore(unittest.TestCase):

    def setUp(self):
        map(lambda mock: mock.reset_mock(), mocks)

    def test_gen_time(self):
        s = datetime.datetime(2012, 1, 1)
        e = datetime.datetime(2012, 1, 1, 11, 59, 59)
        i = datetime.timedelta(hours=2)

        expected = [datetime.datetime(2012, 1, 1, hour, 0, 0)
                    for hour in [0, 2, 4, 6, 8, 10]]

        result = [t for t in core.gen_time(s, e, i)]

        self.assertEqual(result, expected)

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

    @patch('xivo_dao.stat_queue_periodic_dao.get_most_recent_time',
           mock_get_most_recent_time)
    def test_get_start_time_has_call_on_queue_entry(self):
        mock_get_most_recent_time.return_value = datetime.datetime(2012, 1, 1, 1, 23, 54)

        expected = datetime.datetime(2011, 12, 31, 2, 0, 0)

        result = core.get_start_time()

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_queue_periodic_dao.get_most_recent_time',
           mock_get_most_recent_time)
    @patch('xivo_dao.queue_log_dao.get_first_time', mock_get_first_time)
    def test_get_start_time_no_call_on_queue(self):
        mock_get_most_recent_time.side_effect = LookupError('Empty table')
        mock_get_first_time.return_value = datetime.datetime(2012, 1, 1, 1, 12, 23, 666)

        expected = datetime.datetime(2011, 12, 31, 1, 0, 0)

        result = core.get_start_time()

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_queue_periodic_dao.get_most_recent_time',
           mock_get_most_recent_time)
    @patch('xivo_dao.queue_log_dao.get_first_time', mock_get_first_time)
    def test_get_start_time_no_data(self):
        mock_get_most_recent_time.side_effect = LookupError('Empty table')
        mock_get_first_time.side_effect = LookupError('Empty table')

        self.assertRaises(RuntimeError, core.get_start_time)

    def test_get_end_time(self):
        now = datetime.datetime.now()

        expected = datetime.datetime(now.year,
                                     now.month,
                                     now.day,
                                     now.hour - 1,
                                     59, 59, 999999)

        result = core.get_end_time()

        self.assertEqual(result, expected)

    @patch('xivo_stat.core.get_start_time', mock_start_time)
    @patch('xivo_stat.core.get_end_time', mock_end_time)
    def test_get_start_end_time(self):
        s = datetime.datetime(2012, 1, 1)
        e = datetime.datetime(2012, 1, 2)
        mock_start_time.return_value = s
        mock_end_time.return_value = e

        expected = s, e

        result = core.get_start_end_time()

        self.assertEqual(result, expected)

    @patch('xivo_stat.core.get_start_time', mock_start_time)
    @patch('xivo_stat.core.get_end_time', mock_end_time)
    @patch('xivo_stat.queue.fill_calls', mock_fill_calls)
    @patch('xivo_stat.queue.insert_periodic_stat',
           mock_insert_periodic_stat)
    @patch('xivo_stat.core.insert_missing_queues', mock_insert_missing_queues)
    @patch('xivo_stat.core.insert_missing_agents', mock_insert_missing_agents)
    def test_update_db(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 4, 59, 59, 999999)
        mock_start_time.return_value = start
        mock_end_time.return_value = end

        core.update_db()

        mock_insert_missing_queues.assert_called_once_with(start, end)
        mock_insert_missing_agents.assert_called_once_with(start)
        mock_fill_calls.assert_called_once_with(start, end)
        mock_insert_periodic_stat.assert_called_once_with(start, end)

    @patch('xivo_dao.stat_call_on_queue_dao.clean_table', mock_clean_table_stat_call_on_queue)
    @patch('xivo_dao.stat_queue_periodic_dao.clean_table', mock_clean_table_stat_queue_periodic)
    def test_clean_db(self):
        core.clean_db()

        mock_clean_table_stat_call_on_queue.assert_called_with()
        mock_clean_table_stat_queue_periodic.assert_called_with()

    @patch('xivo_dao.queue_log_dao.get_queue_names_in_range', mock_get_queue_names_in_range)
    @patch('xivo_dao.stat_queue_dao.insert_if_missing', mock_insert_if_missing)
    def test_insert_missing_queues(self):
        start = datetime.datetime(2012, 1, 1, 1, 1, 1)
        end = datetime.datetime(2012, 1, 2, 1, 1, 1)
        queue_names = ['queue_%s' % x for x in range(10)]
        mock_get_queue_names_in_range.return_value = queue_names

        core.insert_missing_queues(start, end)

        mock_insert_if_missing.assert_called_once_with(queue_names)

    @patch('xivo_dao.stat_agent_dao.insert_if_missing', mock_insert_agent_if_missing)
    @patch('xivo_dao.queue_log_dao.get_agents_after', mock_get_agents_after)
    def test_insert_missing_agents(self):
        start = datetime.datetime(2012, 1, 1)
        agents = ['Agent/1', 'Agent/2']
        mock_get_agents_after.return_value = agents

        core.insert_missing_agents(start)

        mock_insert_agent_if_missing.assert_called_once_with(agents)
        mock_get_agents_after.assert_called_once_with(start)
