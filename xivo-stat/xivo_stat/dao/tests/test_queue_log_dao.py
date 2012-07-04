# -*- coding: UTF-8 -*-

import unittest
from xivo_stat.dao import queue_log_dao
from xivo_stat.dao.alchemy.queue_log import QueueLog
from xivo_stat.dao.alchemy import dbconnection
from xivo_stat.dao.alchemy.base import Base
import datetime


class TestQueueLogDAO(unittest.TestCase):

    tables = [QueueLog]

    @classmethod
    def setUpClass(cls):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        cls.session = connection.get_session()

        engine = connection.get_engine()
        Base.metadata.drop_all(engine, [table.__table__ for table in cls.tables])
        Base.metadata.create_all(engine, [table.__table__ for table in cls.tables])
        engine.dispose()

    @classmethod
    def tearDownClass(cls):
        dbconnection.unregister_db_connection_pool()

    def _empty_tables(self):
        for table in self.tables:
            entries = self.session.query(table)
            if entries.count() > 0:
                map(self.session.delete, entries)

    def setUp(self):
        self._empty_tables()

    def _insert_entry_queue_full(self, datetimewithmicro, queuename):
        queue_log = QueueLog()
        queue_log.time = datetimewithmicro
        queue_log.queuename = queuename
        queue_log.event = 'FULL'
        self.session.add(queue_log)
        self.session.commit()

    def test_get_queue_full_call(self):
        queuename = 'q1'
        for minute in [10, 20, 30, 40, 50]:
            datetimewithmicro = datetime.datetime(2012, 01, 01, 00, minute, 00)
            self._insert_entry_queue_full(datetimewithmicro, queuename)
        expected_result = []

        datetimestart = datetime.datetime(2012, 01, 01, 00, 00, 00)
        datetimeend = datetime.datetime(2012, 01, 01, 00, 59, 59)
        result = queue_log_dao.get_queue_full_call(datetimestart, datetimeend, queuename)

        self.assertEqual(result, expected_result)
