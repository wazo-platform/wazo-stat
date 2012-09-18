# -*- coding: utf-8 -*-

import unittest

from datetime import datetime
from datetime import timedelta

from xivo_stat import core
from xivo_stat import time_utils


class TestTimeUtils(unittest.TestCase):


    def test_get_period_start_for_time_range(self):
        time_list = [
            datetime(2012, 1, 1, 1),
            datetime(2012, 1, 1, 2),
            datetime(2012, 1, 1, 3),
            datetime(2012, 1, 1, 4),
            datetime(2012, 1, 1, 5),
            ]

        start = datetime(2012, 1, 1, 2, 0, 0)
        end = datetime(2012, 1, 1, 5, 0)

        result = time_utils.get_period_start_for_time_range(
            time_list, start, end)

        expected = [
            datetime(2012, 1, 1, 2),
            datetime(2012, 1, 1, 3),
            datetime(2012, 1, 1, 4),
            ]

        self.assertEqual(result, expected)
