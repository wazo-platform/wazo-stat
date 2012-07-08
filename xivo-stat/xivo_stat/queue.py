# -*- coding: utf-8 -*-
from xivo_dao import queue_log_dao
from xivo_dao import stat_call_on_queue_dao


def fill_full_call(start, end):
    full_calls = queue_log_dao.get_queue_full_call(start, end)
    for call in full_calls:
        stat_call_on_queue_dao.add_full_call(call['callid'],
                                             call['time'],
                                             call['queue_name'])


def fill_calls(start, end):
    fill_full_call(start, end)


def insert_periodic_stat(start, end):
    pass
