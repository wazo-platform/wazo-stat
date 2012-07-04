# -*- coding: UTF-8 -*-

from xivo_stat.dao.alchemy.queue_log import QueueLog
from xivo_stat.dao.alchemy import dbconnection

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_queue_full_call(start, end, queuename):
    res = _session().query(QueueLog).filter(QueueLog.queuename == queuename)
    if res.count() == 0:
        raise LookupError
    return res
