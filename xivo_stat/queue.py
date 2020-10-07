# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao import queue_log_dao
from xivo_dao import stat_dao
from xivo_dao import stat_call_on_queue_dao
from xivo_dao import stat_queue_periodic_dao

logger = logging.getLogger(__name__)


def fill_abandoned_call(dao_sess, start, end):
    abandoned_calls = queue_log_dao.get_queue_abandoned_call(dao_sess, start, end)
    for call in abandoned_calls:
        stat_call_on_queue_dao.add_abandoned_call(dao_sess,
                                                  call['callid'],
                                                  call['time'],
                                                  call['queue_name'],
                                                  call['waittime'])


def fill_timeout_call(dao_sess, start, end):
    timeout_calls = queue_log_dao.get_queue_timeout_call(dao_sess, start, end)
    for call in timeout_calls:
        stat_call_on_queue_dao.add_timeout_call(dao_sess,
                                                call['callid'],
                                                call['time'],
                                                call['queue_name'],
                                                call['waittime'])


def fill_calls(dao_sess, start, end):
    fill_abandoned_call(dao_sess, start, end)
    fill_timeout_call(dao_sess, start, end)


def fill_simple_calls(dao_sess, start, end):
    logger.info('Inserting simple calls...')
    stat_dao.fill_simple_calls(dao_sess, start, end)
    logger.info('Inserting answered calls...')
    stat_dao.fill_answered_calls(dao_sess, start, end)
    logger.info('Inserting leaveempty calls...')
    stat_dao.fill_leaveempty_calls(dao_sess, start, end)


def insert_periodic_stat(dao_sess, start, end):
    periodic_stats = stat_call_on_queue_dao.get_periodic_stats_hour(dao_sess, start, end)
    dao_sess.flush()

    for period, stats in periodic_stats.items():
        logger.info('Inserting queue periodic stat %s', period)
        stat_queue_periodic_dao.insert_stats(dao_sess, stats, period)
    dao_sess.flush()


def remove_between(dao_sess, start, end):
    logger.info('Removing queue cache between %s - %s', start, end)
    callids = stat_call_on_queue_dao.find_all_callid_between_date(dao_sess, start, end)
    if callids:
        stat_call_on_queue_dao.remove_callids(dao_sess, callids)
    stat_queue_periodic_dao.remove_after(dao_sess, start)
