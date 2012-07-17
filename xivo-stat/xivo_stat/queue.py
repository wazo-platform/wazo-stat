# -*- coding: utf-8 -*-
import datetime
import xivo_stat

from xivo_dao import queue_log_dao
from xivo_dao import stat_call_on_queue_dao
from xivo_dao import stat_queue_periodic_dao


def fill_full_call(start, end):
    full_calls = queue_log_dao.get_queue_full_call(start, end)
    for call in full_calls:
        stat_call_on_queue_dao.add_full_call(call['callid'],
                                             call['time'],
                                             call['queue_name'])


def fill_joinempty_call(start, end):
    joinempty_calls = queue_log_dao.get_queue_joinempty_call(start, end)
    for call in joinempty_calls:
        stat_call_on_queue_dao.add_joinempty_call(call['callid'],
                                                  call['time'],
                                                  call['queue_name'])


def fill_leaveempty_call(start, end):
    leaveempty_calls = queue_log_dao.get_queue_leaveempty_call(start, end)
    for call in leaveempty_calls:
        stat_call_on_queue_dao.add_leaveempty_call(call['callid'],
                                                   call['time'],
                                                   call['queue_name'])


def fill_abandoned_call(start, end):
    abandoned_calls = queue_log_dao.get_queue_abandoned_call(start, end)
    for call in abandoned_calls:
        stat_call_on_queue_dao.add_abandoned_call(call['callid'],
                                                  call['time'],
                                                  call['queue_name'])


def fill_closed_call(start, end):
    closed_calls = queue_log_dao.get_queue_closed_call(start, end)
    for call in closed_calls:
        stat_call_on_queue_dao.add_closed_call(call['callid'],
                                               call['time'],
                                               call['queue_name'])


def fill_answered_call(start, end):
    answered_calls = queue_log_dao.get_queue_answered_call(start, end)
    for call in answered_calls:
        stat_call_on_queue_dao.add_answered_call(call['callid'],
                                                 call['time'],
                                                 call['queue_name'])


def fill_timeout_call(start, end):
    timeout_calls = queue_log_dao.get_queue_timeout_call(start, end)
    for call in timeout_calls:
        stat_call_on_queue_dao.add_timeout_call(call['callid'],
                                                call['time'],
                                                call['queue_name'])


def fill_calls(start, end):
    fill_abandoned_call(start, end)
    fill_answered_call(start, end)
    fill_closed_call(start, end)
    fill_full_call(start, end)
    fill_joinempty_call(start, end)
    fill_leaveempty_call(start, end)
    fill_timeout_call(start, end)


def insert_periodic_stat(start, end):
    period = datetime.timedelta(hours=1)
    for t in xivo_stat.core.gen_time(start, end, period):
        stats = stat_call_on_queue_dao.get_periodic_stats(t, t + period - datetime.timedelta(microseconds=1))
        stat_queue_periodic_dao.insert_stats(stats, t,)
