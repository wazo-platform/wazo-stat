# -*- coding: UTF-8 -*-
import datetime

from xivo_dao import queue_log_dao
from xivo_dao import stat_call_on_queue_dao


def fill_full_call(start, end):
    full_calls = queue_log_dao.get_queue_full_call(start, end)
    for call in full_calls:
        stat_call_on_queue_dao.add_full_call(call['callid'],
                                             call['time'],
                                             call['queue_name'])


def fill_stats():
    most_recent = stat_call_on_queue_dao.get_most_recent_time()
    now = datetime.datetime.now()
    start = datetime.datetime(most_recent.year,
                              most_recent.month,
                              most_recent.day,
                              most_recent.hour)
    end = datetime.datetime(now.year,
                            now.month,
                            now.day,
                            now.hour - 1)
    fill_full_call(start, end)
