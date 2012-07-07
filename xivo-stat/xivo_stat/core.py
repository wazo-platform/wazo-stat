# -*- coding: utf-8 -*-
import datetime


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
