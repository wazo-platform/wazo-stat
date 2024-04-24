# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import unittest
from unittest.mock import call, patch

from xivo_dao.helpers.db_manager import daosession

from wazo_stat import queue


@daosession
def _session(session):
    return session


class TestQueue(unittest.TestCase):
    def setUp(self):
        self._queue_name = 'my_queue'
        self._dao_sess = _session()

    @patch('xivo_dao.queue_log_dao.get_queue_abandoned_call')
    @patch('xivo_dao.stat_call_on_queue_dao.add_abandoned_call')
    def test_fill_abandoned(self, mock_add_abandoned_call, mock_get_abandoned_call):
        d1 = datetime.datetime(2012, 1, 1).strftime("%Y-%m-%d %H:%M:%S.%f")
        d2 = datetime.datetime(2012, 1, 1, 23, 59, 59, 999999).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
        callid = '1234567.890'
        callid2 = '1234567.891'
        callid3 = '1234567.892'
        waittime = 3
        mock_get_abandoned_call.return_value = [
            {
                'queue_name': self._queue_name,
                'event': 'abandoned',
                'time': d1,
                'callid': callid,
                'waittime': waittime,
            },
            # should be ignored
            {
                'queue_name': self._queue_name,
                'event': 'abandoned',
                'time': d1,
                'callid': callid2,
                'waittime': None,
            },
            # should pass
            {
                'queue_name': self._queue_name,
                'event': 'abandoned',
                'time': d1,
                'callid': callid3,
                'waittime': 0,
            },
        ]

        queue.fill_abandoned_call(self._dao_sess, d1, d2)

        mock_add_abandoned_call.assert_has_calls(
            [
                call(self._dao_sess, callid, d1, self._queue_name, waittime),
                call(self._dao_sess, callid3, d1, self._queue_name, 0),
            ]
        )

    @patch('xivo_dao.queue_log_dao.get_queue_timeout_call')
    @patch('xivo_dao.stat_call_on_queue_dao.add_timeout_call')
    def test_fill_timeout(self, mock_add_timeout_call, mock_get_timeout_call):
        d1 = datetime.datetime(2012, 1, 1).strftime("%Y-%m-%d %H:%M:%S.%f")
        d2 = datetime.datetime(2012, 1, 1, 23, 59, 59, 999999).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
        callid = '1234567.890'
        callid2 = '1234567.891'
        callid3 = '1234567.892'
        waittime = 7
        mock_get_timeout_call.return_value = [
            {
                'queue_name': self._queue_name,
                'event': 'timeout',
                'time': d1,
                'callid': callid,
                'waittime': waittime,
            },
            # should be ignored
            {
                'queue_name': self._queue_name,
                'event': 'timeout',
                'time': d1,
                'callid': callid2,
                'waittime': None,
            },
            # should pass
            {
                'queue_name': self._queue_name,
                'event': 'timeout',
                'time': d1,
                'callid': callid3,
                'waittime': 0,
            },
        ]

        queue.fill_timeout_call(self._dao_sess, d1, d2)

        mock_add_timeout_call.assert_has_calls(
            [
                call(self._dao_sess, callid, d1, self._queue_name, waittime),
                call(self._dao_sess, callid3, d1, self._queue_name, 0),
            ]
        )

    @patch('wazo_stat.queue.fill_abandoned_call')
    @patch('wazo_stat.queue.fill_timeout_call')
    def test_fill_calls(self, mock_fill_timeout_call, mock_fill_abandoned_call):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 4, 59, 59, 999999)

        queue.fill_calls(self._dao_sess, start, end)

        mock_fill_abandoned_call.assert_called_once_with(self._dao_sess, start, end)
        mock_fill_timeout_call.assert_called_once_with(self._dao_sess, start, end)

    @patch('xivo_dao.stat_dao.fill_simple_calls')
    @patch('xivo_dao.stat_dao.fill_answered_calls')
    @patch('xivo_dao.stat_dao.fill_leaveempty_calls')
    def test_fill_simple_calls(self, fill_simple, fill_answered, fill_leaveempty):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 4, 59, 59, 999999)

        queue.fill_simple_calls(self._dao_sess, start, end)

        fill_simple.assert_called_once_with(self._dao_sess, start, end)
        fill_answered.assert_called_once_with(self._dao_sess, start, end)
        fill_leaveempty.assert_called_once_with(self._dao_sess, start, end)

    @patch('xivo_dao.stat_call_on_queue_dao.get_periodic_stats_hour')
    @patch('xivo_dao.stat_queue_periodic_dao.insert_stats')
    def test_insert_periodic_stat(self, mock_insert_stats, mock_get_periodic_stats):
        s = datetime.datetime(2012, 1, 1)
        e = datetime.datetime(2012, 1, 31, 23, 59, 59, 999999)

        t1 = s
        t2 = s + datetime.timedelta(hours=1)

        stat1 = {'stats': 1234}
        stat2 = {'stats': 5555}

        fake_stats = {t1: stat1, t2: stat2}

        mock_get_periodic_stats.return_value = fake_stats

        queue.insert_periodic_stat(self._dao_sess, s, e)

        mock_insert_stats.assert_any_call(self._dao_sess, stat1, t1)
        mock_insert_stats.assert_any_call(self._dao_sess, stat2, t2)
        self.assertEqual(mock_insert_stats.call_count, 2)

    @patch('xivo_dao.stat_call_on_queue_dao.remove_callids')
    @patch('xivo_dao.stat_call_on_queue_dao.find_all_callid_between_date')
    @patch('xivo_dao.stat_queue_periodic_dao.remove_after')
    def test_remove_between(
        self,
        mock_stat_queue_periodic_remove_after,
        mock_find_all_callid_between_date,
        mock_remove_callids,
    ):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 23, 59, 59)
        callids = [1, 2, 3]

        mock_find_all_callid_between_date.return_value = callids

        queue.remove_between(self._dao_sess, start, end)

        mock_find_all_callid_between_date.assert_called_once_with(
            self._dao_sess, start, end
        )
        mock_remove_callids.assert_called_once_with(self._dao_sess, callids)
        mock_stat_queue_periodic_remove_after.assert_called_once_with(
            self._dao_sess, start
        )

    @patch('xivo_dao.stat_call_on_queue_dao.remove_callids')
    @patch('xivo_dao.stat_call_on_queue_dao.find_all_callid_between_date')
    @patch('xivo_dao.stat_queue_periodic_dao.remove_after')
    def test_remove_between_no_calls(
        self,
        mock_stat_queue_periodic_remove_after,
        mock_find_all_callid_between_date,
        mock_remove_callids,
    ):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 23, 59, 59)
        callids = []

        mock_find_all_callid_between_date.return_value = callids

        queue.remove_between(self._dao_sess, start, end)

        mock_find_all_callid_between_date.assert_called_once_with(
            self._dao_sess, start, end
        )
        self.assertEqual(mock_remove_callids.call_count, 0)
        mock_stat_queue_periodic_remove_after.assert_called_once_with(
            self._dao_sess, start
        )
