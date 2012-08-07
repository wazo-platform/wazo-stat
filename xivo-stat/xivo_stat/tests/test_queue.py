# -*- coding: UTF-8 -*-
import datetime
import unittest

from mock import Mock, patch

from xivo_stat import queue


mock_add_abandoned_call = Mock()
mock_add_answered_call = Mock()
mock_add_closed_call = Mock()
mock_add_full_call = Mock()
mock_add_joinempty_call = Mock()
mock_add_leaveempty_call = Mock()
mock_add_timeout_call = Mock()
mock_fill_abandoned_call = Mock()
mock_fill_answered_call = Mock()
mock_fill_closed_call = Mock()
mock_fill_full_call = Mock()
mock_fill_joinempty_call = Mock()
mock_fill_leaveempty_call = Mock()
mock_fill_timeout_call = Mock()
mock_get_abandoned_call = Mock()
mock_get_closed_call = Mock()
mock_get_full_call = Mock()
mock_get_joinempty_call = Mock()
mock_get_leaveempty_call = Mock()
mock_get_timeout_call = Mock()
mock_get_most_recent_time = Mock()
mock_get_periodic_stats = Mock()
mock_insert_periodic_stat = Mock()
mock_insert_stats = Mock()
mock_stat_call_on_queue_remove_after = Mock()
mock_stat_queue_periodic_remove_after = Mock()


mocks = [mock_add_abandoned_call,
         mock_add_answered_call,
         mock_add_closed_call,
         mock_add_full_call,
         mock_add_joinempty_call,
         mock_add_leaveempty_call,
         mock_fill_abandoned_call,
         mock_fill_answered_call,
         mock_fill_closed_call,
         mock_fill_full_call,
         mock_fill_joinempty_call,
         mock_fill_leaveempty_call,
         mock_fill_timeout_call,
         mock_get_abandoned_call,
         mock_get_closed_call,
         mock_get_full_call,
         mock_get_joinempty_call,
         mock_get_leaveempty_call,
         mock_get_most_recent_time,
         mock_get_periodic_stats,
         mock_insert_periodic_stat,
         mock_insert_stats,
         mock_stat_call_on_queue_remove_after,
         mock_stat_queue_periodic_remove_after,
         ]


class TestQueue(unittest.TestCase):

    def setUp(self):
        self._queue_name = 'my_queue'
        map(lambda mock: mock.reset_mock(), mocks)

    @patch('xivo_dao.queue_log_dao.get_queue_full_call',
           mock_get_full_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_full_call',
           mock_add_full_call)
    def test_fill_full(self):
        d1 = (datetime.datetime(2012, 01, 01)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 01, 01, 23, 59, 59, 999999)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        callid = '1234567.890'
        mock_get_full_call.return_value = [{'queue_name': self._queue_name,
                                            'event': 'full',
                                            'time': d1,
                                            'callid': callid}]

        queue.fill_full_call(d1, d2)

        mock_add_full_call.assert_called_once_with(callid, d1, self._queue_name)

    @patch('xivo_dao.queue_log_dao.get_queue_closed_call',
           mock_get_closed_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_closed_call',
           mock_add_closed_call)
    def test_fill_closed(self):
        d1 = (datetime.datetime(2012, 01, 01)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 01, 01, 23, 59, 59, 999999)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        callid = '1234567.890'
        mock_get_closed_call.return_value = [{'queue_name': self._queue_name,
                                              'event': 'closed',
                                              'time': d1,
                                              'callid': callid}]

        queue.fill_closed_call(d1, d2)

        mock_add_closed_call.assert_called_once_with(callid, d1, self._queue_name)

    @patch('xivo_dao.queue_log_dao.get_queue_abandoned_call',
           mock_get_abandoned_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_abandoned_call',
           mock_add_abandoned_call)
    def test_fill_abandoned(self):
        d1 = (datetime.datetime(2012, 01, 01)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 01, 01, 23, 59, 59, 999999)
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

    @patch('xivo_dao.queue_log_dao.get_queue_joinempty_call',
           mock_get_joinempty_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_joinempty_call',
           mock_add_joinempty_call)
    def test_fill_joinempty(self):
        d1 = (datetime.datetime(2012, 01, 01)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 01, 01, 23, 59, 59, 999999)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        callid = '1234567.890'
        mock_get_joinempty_call.return_value = [{'queue_name': self._queue_name,
                                                 'event': 'joinempty',
                                                 'time': d1,
                                                 'callid': callid}]

        queue.fill_joinempty_call(d1, d2)

        mock_add_joinempty_call.assert_called_once_with(callid, d1, self._queue_name)

    @patch('xivo_dao.queue_log_dao.get_queue_leaveempty_call',
           mock_get_leaveempty_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_leaveempty_call',
           mock_add_leaveempty_call)
    def test_fill_leaveempty(self):
        d1 = (datetime.datetime(2012, 01, 01)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 01, 01, 23, 59, 59, 999999)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        callid = '1234567.890'
        waittime = 11
        mock_get_leaveempty_call.return_value = [{'queue_name': self._queue_name,
                                                  'event': 'leaveempty',
                                                  'time': d1,
                                                  'callid': callid,
                                                  'waittime': waittime}]

        queue.fill_leaveempty_call(d1, d2)

        mock_add_leaveempty_call.assert_called_once_with(callid, d1, self._queue_name, waittime)

    @patch('xivo_dao.queue_log_dao.get_queue_timeout_call',
           mock_get_timeout_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_timeout_call',
           mock_add_timeout_call)
    def test_fill_timeout(self):
        d1 = (datetime.datetime(2012, 01, 01)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 01, 01, 23, 59, 59, 999999)
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

    @patch('xivo_stat.queue.fill_abandoned_call', mock_fill_abandoned_call)
    @patch('xivo_stat.queue.fill_answered_call', mock_fill_answered_call)
    @patch('xivo_stat.queue.fill_closed_call', mock_fill_closed_call)
    @patch('xivo_stat.queue.fill_full_call', mock_fill_full_call)
    @patch('xivo_stat.queue.fill_joinempty_call', mock_fill_joinempty_call)
    @patch('xivo_stat.queue.fill_leaveempty_call', mock_fill_leaveempty_call)
    @patch('xivo_stat.queue.fill_timeout_call', mock_fill_timeout_call)
    def test_fill_calls(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 4, 59, 59, 999999)
        queue.fill_calls(start, end)

        mock_fill_abandoned_call.assert_called_once_with(start, end)
        mock_fill_answered_call.assert_called_once_with(start, end)
        mock_fill_closed_call.assert_called_once_with(start, end)
        mock_fill_full_call.assert_called_once_with(start, end)
        mock_fill_timeout_call.assert_called_once_with(start, end)
        mock_fill_joinempty_call.assert_called_once_with(start, end)
        mock_fill_leaveempty_call.assert_called_once_with(start, end)

    @patch('xivo_dao.stat_call_on_queue_dao.get_periodic_stats',
           mock_get_periodic_stats)
    @patch('xivo_dao.stat_queue_periodic_dao.insert_stats', mock_insert_stats)
    def test_insert_periodic_stat(self):
        s = datetime.datetime(2012, 01, 01)
        e = datetime.datetime(2012, 01, 31, 23, 59, 59, 999999)

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

    @patch('xivo_dao.stat_call_on_queue_dao.remove_after', mock_stat_call_on_queue_remove_after)
    @patch('xivo_dao.stat_queue_periodic_dao.remove_after', mock_stat_queue_periodic_remove_after)
    def test_remove_after_start(self):
        s = datetime.datetime(2012, 1, 1)

        queue.remove_after_start(s)

        mock_stat_call_on_queue_remove_after.assert_called_once_with(s)
        mock_stat_queue_periodic_remove_after.assert_called_once_with(s)
