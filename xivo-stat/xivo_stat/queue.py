# -*- coding: utf-8 -*-
import datetime

from xivo_dao import queue_log_dao
from xivo_dao import stat_call_on_queue_dao
from xivo_dao import stat_queue_periodic_dao
import xivo_stat


def fill_full_call(start, end):
    full_calls = queue_log_dao.get_queue_full_call(start, end)
    for call in full_calls:
        stat_call_on_queue_dao.add_full_call(call['callid'],
                                             call['time'],
                                             call['queue_name'])


def fill_calls(start, end):
    fill_full_call(start, end)


def insert_periodic_stat(start, end):
    period = datetime.timedelta(hours=1)
    for t in xivo_stat.core.gen_time(start, end, period):
        stats = stat_call_on_queue_dao.get_periodic_stats(t, t + period - datetime.timedelta(microseconds=1))
        stat_queue_periodic_dao.insert_stats(stats, t,)
