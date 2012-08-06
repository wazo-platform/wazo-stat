# -*- coding: utf-8 -*-
from xivo_dao import queue_log_dao
from xivo_dao import stat_call_on_queue_dao
from xivo_dao import stat_queue_periodic_dao


def fill_full_call(started_calls):
    full_calls = filter(lambda c: c.event == 'FULL', started_calls)
    for c in full_calls:
        stat_call_on_queue_dao.add_full_call(c.callid, c.time, c.queuename)


def fill_joinempty_call(started_calls):
    joinempty_calls = filter(lambda c: c.event == 'JOINEMPTY', started_calls)
    for c in joinempty_calls:
        stat_call_on_queue_dao.add_joinempty_call(c.callid, c.time, c.queuename)


def fill_leaveempty_call(started_calls):
    leaveempty_calls = queue_log_dao.get_queue_leaveempty_call(started_calls)
    for call in leaveempty_calls:
        stat_call_on_queue_dao.add_leaveempty_call(call['callid'],
                                                   call['time'],
                                                   call['queue_name'],
                                                   call['waittime'])


def fill_abandoned_call(started_calls):
    abandoned_calls = queue_log_dao.get_queue_abandoned_call(started_calls)
    for call in abandoned_calls:
        stat_call_on_queue_dao.add_abandoned_call(call['callid'],
                                                  call['time'],
                                                  call['queue_name'],
                                                  call['waittime'])


def fill_closed_call(started_calls):
    closed_calls = filter(lambda c: c.event == 'CLOSED', started_calls)
    for c in closed_calls:
        stat_call_on_queue_dao.add_closed_call(c.callid, c.time, c.queuename)


def fill_answered_call(started_calls):
    answered_calls = queue_log_dao.get_queue_answered_call(started_calls)
    for call in answered_calls:
        stat_call_on_queue_dao.add_answered_call(
            call['callid'],
            call['time'],
            call['queue_name'],
            call['agent'],
            call['waittime'],
            call['talktime'],
            )


def fill_timeout_call(started_calls):
    timeout_calls = queue_log_dao.get_queue_timeout_call(started_calls)
    for call in timeout_calls:
        stat_call_on_queue_dao.add_timeout_call(call['callid'],
                                                call['time'],
                                                call['queue_name'],
                                                call['waittime'])


def fill_calls(start, end):
    started_calls = queue_log_dao.get_started_calls(start, end)

    fill_abandoned_call(started_calls)
    fill_answered_call(started_calls)
    fill_closed_call(started_calls)
    fill_full_call(started_calls)
    fill_joinempty_call(started_calls)
    fill_leaveempty_call(started_calls)
    fill_timeout_call(started_calls)


def insert_periodic_stat(start, end):
    stats = stat_call_on_queue_dao.get_periodic_stats(start, end)
    for period, stat in stats.iteritems():
        stat_queue_periodic_dao.insert_stats(stat, period)


def remove_after_start(start):
    stat_call_on_queue_dao.remove_after(start)
    stat_queue_periodic_dao.remove_after(start)
