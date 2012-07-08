# -*- coding: utf-8 -*-
import unittest
import datetime
from mock import Mock
from mock import patch
from xivo_stat import core

mock_end_time = Mock()
mock_fill_calls = Mock()
mock_get_first_time = Mock()
mock_get_most_recent_time = Mock()
mock_insert_periodic_stat = Mock()
mock_start_time = Mock()

mocks = [mock_end_time,
         mock_fill_calls,
         mock_get_first_time,
         mock_get_most_recent_time,
         mock_insert_periodic_stat,
         mock_start_time]


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

    @patch('xivo_dao.stat_call_on_queue_dao.get_most_recent_time',
           mock_get_most_recent_time)
    def test_get_start_time_has_call_on_queue_entry(self):
        mock_get_most_recent_time.return_value = datetime.datetime(2012, 1, 1, 1, 23, 54)

        expected = datetime.datetime(2012, 1, 1, 1, 0, 0)

        result = core.get_start_time()

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_call_on_queue_dao.get_most_recent_time',
           mock_get_most_recent_time)
    @patch('xivo_dao.queue_log_dao.get_first_time', mock_get_first_time)
    def test_get_start_time_no_call_on_queue(self):
        mock_get_most_recent_time.side_effect = LookupError('Empty table')
        mock_get_first_time.return_value = datetime.datetime(2012, 1, 1, 1, 12, 23, 666)

        expected = datetime.datetime(2012, 1, 1, 1, 0, 0)

        result = core.get_start_time()

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_call_on_queue_dao.get_most_recent_time',
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
    def test_update_db(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 4, 59, 59, 999999)
        mock_start_time.return_value = start
        mock_end_time.return_value = end

        core.update_db()

        mock_fill_calls.assert_called_once_with(start, end)
        mock_insert_periodic_stat.assert_called_once_with(start, end)
