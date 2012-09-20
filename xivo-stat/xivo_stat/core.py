# -*- coding: utf-8 -*-

import datetime
import sys

from xivo_stat import queue
from xivo_stat import agent
from xivo_dao import stat_queue_periodic_dao
from xivo_dao import stat_agent_periodic_dao
from xivo_dao import stat_call_on_queue_dao
from xivo_dao import queue_log_dao
from xivo_dao import stat_queue_dao
from xivo_dao import stat_agent_dao
from sqlalchemy.exc import IntegrityError
from xivo_dao.alchemy import dbconnection


_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


DELTA_1HOUR = datetime.timedelta(hours=1)


def hour_start(t):
    return datetime.datetime(t.year,
                             t.month,
                             t.day,
                             t.hour)


def end_of_previous_hour(t):
    return hour_start(t) - datetime.timedelta(microseconds=1)


def get_start_time():
    try:
        start = hour_start(stat_queue_periodic_dao.get_most_recent_time()) + DELTA_1HOUR
    except LookupError:
        try:
            start = hour_start(queue_log_dao.get_first_time())
        except LookupError:
            raise RuntimeError('No data to generate stats from')
    return start - datetime.timedelta(days=1)


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
        insert_missing_agents(start)
        queue.remove_after_start(start)
        agent.remove_after_start(start)
        queue.fill_simple_calls(start, end)
        agent.insert_periodic_stat(start, end)
        for period_start in queue_log_dao.hours_with_calls(start, end):
            period_end = period_start + datetime.timedelta(hours=1) - datetime.timedelta(microseconds=1)
            queue.fill_calls(period_start, period_end)
            queue.insert_periodic_stat(period_start, period_end)
    except (IntegrityError, KeyboardInterrupt):
        _clean_up_after_error()


def clean_db():
    stat_call_on_queue_dao.clean_table()
    stat_queue_periodic_dao.clean_table()
    stat_agent_periodic_dao.clean_table()


def insert_missing_agents(start):
    print 'Inserting missing agents'
    agents = queue_log_dao.get_agents_after(start)
    stat_agent_dao.insert_if_missing(agents)


def insert_missing_queues(start, end):
    print 'Inserting missing queues...'
    queue_names = queue_log_dao.get_queue_names_in_range(start, end)
    stat_queue_dao.insert_if_missing(queue_names)
