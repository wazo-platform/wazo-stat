# -*- coding: UTF-8 -*-

import datetime
import unittest
from mock import Mock, patch
from xivo_stat.queue import queue

get_full_call = Mock()
add_full_call = Mock()


class TestQueue(unittest.TestCase):

    def setUp(self):
        self._queue_name = 'my_queue'

    @patch('xivo_dao.queue_log_dao.get_queue_full_call', get_full_call)
    @patch('xivo_dao.call_on_queue_dao.add_full_call', add_full_call)
    def test_fill_full(self):
        d1 = datetime.datetime(2012, 01, 01, 00, 00, 00, 0000).strftime("%Y-%m-%d %H:%M:%S.%f")
        d2 = datetime.datetime(2012, 01, 01, 23, 59, 59, 9999).strftime("%Y-%m-%d %H:%M:%S.%f")
        callid = '1234567.890'
        get_full_call.return_value = [{'queue_name': self._queue_name,
                                       'event': 'full',
                                       'time': d1,
                                       'callid': callid}]

        queue.fill_full_call(d1, d2)

        add_full_call.assert_called_once_with(callid, d1, self._queue_name)
