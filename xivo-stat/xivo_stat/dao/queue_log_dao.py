# -*- coding: UTF-8 -*-

from xivo_stat.dao.alchemy.queue_log import QueueLog
from xivo_stat.dao.alchemy import dbconnection
from sqlalchemy import and_, between

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def get_queue_full_call(start, end, queuename):
    res = (_session()
           .query(QueueLog.queuename, QueueLog.time, QueueLog.callid)
           .filter(and_(QueueLog.queuename == queuename,
                        between(QueueLog.time, start, end))))
    if res.count() == 0:
        raise LookupError
    return [{'queue_name': r.queuename,
             'event': 'full',
             'time': r.time,
             'callid': r.callid} for r in res]
