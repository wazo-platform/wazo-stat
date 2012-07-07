# -*- coding: utf-8 -*-
import datetime

from xivo_dao import stat_call_on_queue_dao
from xivo_dao import queue_log_dao


def gen_time(start, end, step):
    tmp = start
    while tmp <= end:
        yield tmp
        tmp += step


def hour_start(t):
    return datetime.datetime(t.year,
                             t.month,
                             t.day,
                             t.hour)


def end_of_previous_hour(t):
    return hour_start(t) - datetime.timedelta(microseconds=1)


def get_start_time():
    try:
        return hour_start(stat_call_on_queue_dao.get_most_recent_time())
    except LookupError:
        try:
            return hour_start(queue_log_dao.get_first_time())
        except LookupError:
            raise RuntimeError('No data to generate stats from')


def get_end_time():
    return end_of_previous_hour(datetime.datetime.now())


def get_start_end_time():
    return get_start_time(), get_end_time()
