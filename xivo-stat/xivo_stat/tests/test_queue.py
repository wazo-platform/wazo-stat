# -*- coding: UTF-8 -*-

import datetime
import unittest

from mock import patch

from xivo_stat import queue


class TestQueue(unittest.TestCase):

    def setUp(self):
        self._queue_name = 'my_queue'

    @patch('xivo_dao.queue_log_dao.get_queue_abandoned_call')
    @patch('xivo_dao.stat_call_on_queue_dao.add_abandoned_call')
    def test_fill_abandoned(self, mock_add_abandoned_call, mock_get_abandoned_call):
        d1 = (datetime.datetime(2012, 1, 1)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 1, 1, 23, 59, 59, 999999)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        callid = '1234567.890'
        waittime = 3
        mock_get_abandoned_call.return_value = [{'queue_name': self._queue_name,
                                                 'event': 'abandoned',
                                                 'time': d1,
                                                 'callid': callid,
                                                 'waittime': waittime}]

        queue.fill_abandoned_call(d1, d2)

        mock_add_abandoned_call.assert_called_once_with(callid, d1, self._queue_name, waittime)

    @patch('xivo_dao.queue_log_dao.get_queue_timeout_call')
    @patch('xivo_dao.stat_call_on_queue_dao.add_timeout_call')
    def test_fill_timeout(self, mock_add_timeout_call, mock_get_timeout_call):
        d1 = (datetime.datetime(2012, 1, 1)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 1, 1, 23, 59, 59, 999999)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        callid = '1234567.890'
        waittime = 7
        mock_get_timeout_call.return_value = [{'queue_name': self._queue_name,
                                               'event': 'timeout',
                                               'time': d1,
                                               'callid': callid,
                                               'waittime': waittime}]

        queue.fill_timeout_call(d1, d2)

        mock_add_timeout_call.assert_called_once_with(callid, d1, self._queue_name, waittime)

    @patch('xivo_stat.queue.fill_abandoned_call')
    @patch('xivo_stat.queue.fill_timeout_call')
    def test_fill_calls(self, mock_fill_timeout_call, mock_fill_abandoned_call):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 4, 59, 59, 999999)

        queue.fill_calls(start, end)

        mock_fill_abandoned_call.assert_called_once_with(start, end)
        mock_fill_timeout_call.assert_called_once_with(start, end)

    @patch('xivo_dao.stat_call_on_queue_dao.get_periodic_stats')
    @patch('xivo_dao.stat_queue_periodic_dao.insert_stats')
    def test_insert_periodic_stat(self, mock_insert_stats, mock_get_periodic_stats):
        s = datetime.datetime(2012, 1, 1)
        e = datetime.datetime(2012, 1, 31, 23, 59, 59, 999999)

        t1 = s
        t2 = s + datetime.timedelta(hours=1)

        stat1 = {'stats': 1234}
        stat2 = {'stats': 5555}

        fake_stats = {t1: stat1,
                      t2: stat2}

        mock_get_periodic_stats.return_value = fake_stats

        queue.insert_periodic_stat(s, e)

        mock_insert_stats.assert_any_call(stat1, t1)
        mock_insert_stats.assert_any_call(stat2, t2)
        self.assertEqual(mock_insert_stats.call_count, 2)

    @patch('xivo_dao.stat_call_on_queue_dao.remove_after')
    @patch('xivo_dao.stat_queue_periodic_dao.remove_after')
    def test_remove_after_start(self, mock_stat_queue_periodic_remove_after, mock_stat_call_on_queue_remove_after):
        s = datetime.datetime(2012, 1, 1)

        queue.remove_after_start(s)

        mock_stat_call_on_queue_remove_after.assert_called_once_with(s)
        mock_stat_queue_periodic_remove_after.assert_called_once_with(s)
