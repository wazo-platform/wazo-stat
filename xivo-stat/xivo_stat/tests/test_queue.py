# -*- coding: UTF-8 -*-
import datetime
import unittest

from mock import Mock, patch

from xivo_stat import queue


mock_add_full_call = Mock()
mock_fill_full_call = Mock()
mock_get_full_call = Mock()
mock_get_most_recent_time = Mock()
mock_insert_periodic_stat = Mock()

mocks = [mock_add_full_call,
         mock_fill_full_call,
         mock_get_full_call,
         mock_get_most_recent_time,
         mock_insert_periodic_stat]


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

    @patch('xivo_stat.queue.fill_full_call', mock_fill_full_call)
    def test_fill_calls(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 4, 59, 59, 999999)
        queue.fill_calls(start, end)

        mock_fill_full_call.assert_called_once_with(start, end)
