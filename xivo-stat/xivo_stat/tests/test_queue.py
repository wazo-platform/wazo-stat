# -*- coding: UTF-8 -*-
import datetime
import unittest

from mock import Mock, patch

from xivo_stat import queue
from xivo_dao.queue_log_dao import CallStart


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
mock_get_answered_call = Mock()
mock_get_leaveempty_call = Mock()
mock_get_timeout_call = Mock()
mock_get_most_recent_time = Mock()
mock_get_periodic_stats = Mock()
mock_get_started_calls = Mock()
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
         mock_get_answered_call,
         mock_get_leaveempty_call,
         mock_get_most_recent_time,
         mock_get_periodic_stats,
         mock_get_started_calls,
         mock_insert_periodic_stat,
         mock_insert_stats,
         mock_stat_call_on_queue_remove_after,
         mock_stat_queue_periodic_remove_after,
         ]


class TestQueue(unittest.TestCase):

    def setUp(self):
        self._queue_name = 'my_queue'
        map(lambda mock: mock.reset_mock(), mocks)
        self._started_calls = [
            # Full calls
            CallStart('1', 'FULL', datetime.datetime(2012, 1, 1), self._queue_name),
            CallStart('2', 'FULL', datetime.datetime(2012, 1, 1, 0, 15), self._queue_name),
            # Closed calls
            CallStart('3', 'CLOSED', datetime.datetime(2012, 1, 1, 0, 1), self._queue_name),
            CallStart('4', 'CLOSED', datetime.datetime(2012, 1, 1, 0, 11), self._queue_name),
            # Answered calls
            CallStart('5', 'ENTERQUEUE', datetime.datetime(2012, 1, 1, 0, 12), self._queue_name),
            CallStart('6', 'ENTERQUEUE', datetime.datetime(2012, 1, 1, 0, 13), self._queue_name),
            # Abandoned calls
            CallStart('7', 'ENTERQUEUE', datetime.datetime(2012, 1, 1, 0, 14), self._queue_name),
            CallStart('8', 'ENTERQUEUE', datetime.datetime(2012, 1, 1, 0, 15), self._queue_name),
            # Join empty calls
            CallStart('9', 'JOINEMPTY', datetime.datetime(2012, 1, 1, 0, 16), self._queue_name),
            CallStart('10', 'JOINEMPTY', datetime.datetime(2012, 1, 1, 0, 17), self._queue_name),
            # leaveempty calls
            CallStart('11', 'ENTERQUEUE', datetime.datetime(2012, 1, 1, 0, 18), self._queue_name),
            CallStart('12', 'ENTERQUEUE', datetime.datetime(2012, 1, 1, 0, 19), self._queue_name),
            # Timeout calls
            CallStart('13', 'ENTERQUEUE', datetime.datetime(2012, 1, 1, 0, 20), self._queue_name),
            CallStart('14', 'ENTERQUEUE', datetime.datetime(2012, 1, 1, 0, 21), self._queue_name),
            ]
        mock_get_started_calls.return_value = self._started_calls

    @patch('xivo_dao.stat_call_on_queue_dao.add_full_call',
           mock_add_full_call)
    def test_fill_full(self):
        queue.fill_full_call(self._started_calls)

        mock_add_full_call.assert_any_call(
            '1', datetime.datetime(2012, 1, 1), self._queue_name)
        mock_add_full_call.assert_any_call(
            '2', datetime.datetime(2012, 1, 1, 0, 15), self._queue_name)

    @patch('xivo_dao.stat_call_on_queue_dao.add_closed_call',
           mock_add_closed_call)
    def test_fill_closed(self):
        queue.fill_closed_call(self._started_calls)

        self.assertEqual(mock_add_closed_call.call_count, 2)
        mock_add_closed_call.assert_any_call(
            '3', datetime.datetime(2012, 1, 1, 0, 1), self._queue_name)
        mock_add_closed_call.assert_any_call(
            '4', datetime.datetime(2012, 1, 1, 0, 11), self._queue_name)

    @patch('xivo_dao.queue_log_dao.get_queue_answered_call',
           mock_get_answered_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_answered_call',
           mock_add_answered_call)
    def test_fill_answered(self):
        d1 = datetime.datetime(2012, 1, 1, 0, 11)
        d2 = datetime.datetime(2012, 1, 1, 0, 12)
        t1, t2 = 13, 27
        w1, w2 = 5, 7
        a1 = 'Agent/1003'
        mock_get_answered_call.return_value = [
            {'queue_name': self._queue_name,
             'event': 'answered',
             'time': d1,
             'callid': '5',
             'waittime': w1,
             'talktime': t1,
             'agent': a1,
             },
            {'queue_name': self._queue_name,
             'event': 'answered',
             'time': d2,
             'callid': '6',
             'waittime': w2,
             'talktime': t2,
             'agent': a1,
             },
            ]

        queue.fill_answered_call(self._started_calls)

        mock_get_answered_call.assert_called_once_with(self._started_calls)
        mock_add_answered_call.assert_any_call('5', d1, self._queue_name, a1, w1, t1)
        mock_add_answered_call.assert_any_call('6', d2, self._queue_name, a1, w2, t2)

    @patch('xivo_dao.queue_log_dao.get_queue_abandoned_call',
           mock_get_abandoned_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_abandoned_call',
           mock_add_abandoned_call)
    def test_fill_abandoned(self):
        d1 = datetime.datetime(2012, 01, 01, 0, 13)
        d2 = datetime.datetime(2012, 01, 01, 0, 14)
        w1, w2 = 6, 8
        mock_get_abandoned_call.return_value = [
            {'queue_name': self._queue_name,
             'event': 'abandoned',
             'time': d1,
             'callid': '7',
             'waittime': w1},
            {'queue_name': self._queue_name,
             'event': 'abandoned',
             'time': d2,
             'callid': '8',
             'waittime': w2},
            ]

        queue.fill_abandoned_call(self._started_calls)

        mock_add_abandoned_call.assert_any_call('7', d1, self._queue_name, w1)
        mock_add_abandoned_call.assert_any_call('8', d2, self._queue_name, w2)

    @patch('xivo_dao.stat_call_on_queue_dao.add_joinempty_call',
           mock_add_joinempty_call)
    def test_fill_joinempty(self):
        queue.fill_joinempty_call(self._started_calls)

        mock_add_joinempty_call.assert_any_call(
            '9', datetime.datetime(2012, 1, 1, 0, 16), self._queue_name)
        mock_add_joinempty_call.assert_any_call(
            '10', datetime.datetime(2012, 1, 1, 0, 17), self._queue_name)

    @patch('xivo_dao.queue_log_dao.get_queue_leaveempty_call',
           mock_get_leaveempty_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_leaveempty_call',
           mock_add_leaveempty_call)
    def test_fill_leaveempty(self):
        d1 = datetime.datetime(2012, 01, 01, 0, 18)
        d2 = datetime.datetime(2012, 01, 01, 0, 19)
        w1, w2 = 7, 8
        mock_get_leaveempty_call.return_value = [
            {'queue_name': self._queue_name,
             'event': 'leaveempty',
             'time': d1,
             'callid': '11',
             'waittime': w1},
            {'queue_name': self._queue_name,
             'event': 'leaveempty',
             'time': d2,
             'callid': '12',
             'waittime': w2},
            ]

        queue.fill_leaveempty_call(self._started_calls)

        mock_get_leaveempty_call.assert_called_once_with(self._started_calls)
        self.assertEqual(mock_add_leaveempty_call.call_count, 2)
        mock_add_leaveempty_call.assert_any_call('11', d1, self._queue_name, w1)
        mock_add_leaveempty_call.assert_any_call('12', d2, self._queue_name, w2)

    @patch('xivo_dao.queue_log_dao.get_queue_timeout_call',
           mock_get_timeout_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_timeout_call',
           mock_add_timeout_call)
    def test_fill_timeout(self):
        d1 = datetime.datetime(2012, 01, 01, 0, 20)
        d2 = datetime.datetime(2012, 01, 01, 0, 21)
        w1, w2 = 5, 6
        mock_get_timeout_call.return_value = [
            {'queue_name': self._queue_name,
             'event': 'timeout',
             'time': d1,
             'callid': '13',
             'waittime': w1},
            {'queue_name': self._queue_name,
             'event': 'timeout',
             'time': d2,
             'callid': '14',
             'waittime': w2},
            ]

        queue.fill_timeout_call(self._started_calls)

        self.assertEqual(mock_add_timeout_call.call_count, 2)
        mock_add_timeout_call.assert_any_call('13', d1, self._queue_name, w1)
        mock_add_timeout_call.assert_any_call('14', d2, self._queue_name, w2)

    @patch('xivo_dao.queue_log_dao.get_started_calls', mock_get_started_calls)
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
        mock_get_started_calls.return_value = self._started_calls

        queue.fill_calls(start, end)

        mock_get_started_calls.assert_called_once_with(start, end)

        mock_fill_abandoned_call.assert_called_once_with(self._started_calls)
        mock_fill_answered_call.assert_called_once_with(self._started_calls)
        mock_fill_closed_call.assert_called_once_with(self._started_calls)
        mock_fill_full_call.assert_called_once_with(self._started_calls)
        mock_fill_timeout_call.assert_called_once_with(self._started_calls)
        mock_fill_joinempty_call.assert_called_once_with(self._started_calls)
        mock_fill_leaveempty_call.assert_called_once_with(self._started_calls)

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
