# -*- coding: utf-8 -*-
import unittest
import datetime

from xivo_stat import core


class TestCore(unittest.TestCase):

    def test_gen_time(self):
        s = datetime.datetime(2012, 1, 1)
        e = datetime.datetime(2012, 1, 1, 11, 59, 59)
        i = datetime.timedelta(hours=2)

        expected = [datetime.datetime(2012, 1, 1, hour, 0, 0)
                    for hour in [0, 2, 4, 6, 8, 10]]

        result = [t for t in core.gen_time(s, e, i)]

        self.assertEqual(result, expected)

    def test_hour_start(self):
        t = datetime.datetime(2012, 1, 1, 1, 23, 37)

        expected = datetime.datetime(2012, 1, 1, 1, 0, 0)

        result = core.hour_start(t)

        self.assertEqual(result, expected)

    def test_end_of_previous_hour(self):
        t = datetime.datetime(2012, 1, 1, 1, 23, 37)

        expected = datetime.datetime(2012, 1, 1, 0, 59, 59, 999999)

        result = core.end_of_previous_hour(t)

        self.assertEqual(result, expected)
