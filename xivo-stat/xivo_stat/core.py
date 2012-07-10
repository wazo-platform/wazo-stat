# -*- coding: utf-8 -*-
import datetime
import sys

from xivo_dao import stat_queue_periodic_dao, stat_call_on_queue_dao
from xivo_dao import queue_log_dao
from xivo_dao import stat_queue_dao
from xivo_stat import queue
from sqlalchemy.exc import IntegrityError
from xivo_dao.alchemy import dbconnection

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


DELTA_1HOUR = datetime.timedelta(hours=1)


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
        return hour_start(stat_queue_periodic_dao.get_most_recent_time()) + DELTA_1HOUR
    except LookupError:
        try:
            return hour_start(queue_log_dao.get_first_time())
        except LookupError:
            raise RuntimeError('No data to generate stats from')


def get_end_time():
    return end_of_previous_hour(datetime.datetime.now())


def get_start_end_time():
    return get_start_time(), get_end_time()


def _clean_up_after_error():
    print 'Inconsistent cache, cleaning up...'
    _session().rollback()
    clean_db()
    sys.exit(1)


def update_db():
    try:
        start, end = get_start_end_time()
    except RuntimeError:
        return

    print 'Filling cache into DB'
    try:
        insert_missing_queues(start, end)
        queue.fill_calls(start, end)
        queue.insert_periodic_stat(start, end)
    except (IntegrityError, KeyboardInterrupt):
        _clean_up_after_error()


def clean_db():
    stat_call_on_queue_dao.clean_table()
    stat_queue_periodic_dao.clean_table()


def insert_missing_queues(start, end):
    queue_names = queue_log_dao.get_queue_names_in_range(start, end)
    stat_queue_dao.insert_if_missing(queue_names)
