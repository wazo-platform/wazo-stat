# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import datetime

from wazo_auth_client import Client as AuthClient
from wazo_confd_client import Client as ConfdClient
from xivo_dao import stat_queue_periodic_dao
from xivo_dao import stat_agent_periodic_dao
from xivo_dao import stat_call_on_queue_dao
from xivo_dao import queue_log_dao
from xivo_dao import stat_queue_dao
from xivo_dao import stat_agent_dao
from xivo_dao.helpers.db_utils import session_scope

from wazo_stat import agent, queue

logger = logging.getLogger(__name__)

_ERASE_TIME_WHEN_STARTING = datetime.timedelta(hours=8)
DELTA_1HOUR = datetime.timedelta(hours=1)


def hour_start(t):
    return datetime.datetime(t.year, t.month, t.day, t.hour, tzinfo=t.tzinfo)


def end_of_previous_hour(t):
    return hour_start(t) - datetime.timedelta(microseconds=1)


def get_start_time(dao_sess):
    try:
        start = hour_start(stat_queue_periodic_dao.get_most_recent_time(dao_sess))
    except LookupError:
        try:
            start = hour_start(queue_log_dao.get_first_time(dao_sess))
        except LookupError:
            raise RuntimeError('No data to generate stats from')
    return start - _ERASE_TIME_WHEN_STARTING


def update_db(config, end_date, start_date=None):
    if start_date is None:
        try:
            with session_scope() as dao_sess:
                start = get_start_time(dao_sess)
        except RuntimeError:
            return
    else:
        start = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S%z')

    end = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S%z')

    auth_client = AuthClient(**config['auth'])
    token_data = auth_client.token.new(expiration=300)
    confd_client = ConfdClient(**config['confd'])
    confd_client.set_token(token_data['token'])

    logger.info('Getting objects from wazo-confd...')
    confd_queues = confd_client.queues.list(recurse=True)
    confd_agents = confd_client.agents.list(recurse=True)
    master_tenant = token_data['metadata']['tenant_uuid']
    logger.info('Filling cache into DB')
    logger.info('Start Time: %s, End time: %s', start, end)
    with session_scope() as dao_sess:
        insert_missing_queues(
            dao_sess, start, end, confd_queues['items'], master_tenant
        )
        insert_missing_agents(dao_sess, confd_agents['items'])
        dao_sess.flush()

        queue.remove_between(dao_sess, start, end)
        agent.remove_after_start(dao_sess, start)
        queue.fill_simple_calls(dao_sess, start, end)
        dao_sess.flush()

        logger.info('Inserting agent periodic stat')
        agent.insert_periodic_stat(dao_sess, start, end)

        logger.info('Inserting queue periodic stat')
        for period_start in queue_log_dao.hours_with_calls(dao_sess, start, end):
            period_end = (
                period_start
                + datetime.timedelta(hours=1)
                - datetime.timedelta(microseconds=1)
            )
            queue.fill_calls(dao_sess, period_start, period_end)
            queue.insert_periodic_stat(dao_sess, period_start, period_end)


def clean_db():
    with session_scope() as dao_sess:
        stat_call_on_queue_dao.clean_table(dao_sess)
        stat_agent_periodic_dao.clean_table(dao_sess)
        stat_queue_periodic_dao.clean_table(dao_sess)
        stat_agent_dao.clean_table(dao_sess)
        stat_queue_dao.clean_table(dao_sess)


def insert_missing_agents(dao_sess, confd_agents):
    logger.info('Inserting missing agents...')
    stat_agent_dao.insert_missing_agents(dao_sess, confd_agents)


def insert_missing_queues(dao_sess, start, end, confd_queues, master_tenant):
    logger.info('Inserting missing queues...')
    queue_names = queue_log_dao.get_queue_names_in_range(dao_sess, start, end)
    stat_queue_dao.insert_if_missing(dao_sess, queue_names, confd_queues, master_tenant)
