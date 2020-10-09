# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from datetime import datetime
from datetime import timedelta

from wazo_stat import time_utils


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

        result = time_utils.get_period_start_for_time_range(time_list, start, end)

        expected = [
            datetime(2012, 1, 1, 2),
            datetime(2012, 1, 1, 3),
            datetime(2012, 1, 1, 4),
        ]

        self.assertEqual(result, expected)

    def test_gen_time(self):
        s = datetime(2012, 1, 1)
        e = datetime(2012, 1, 1, 11, 59, 59)
        i = timedelta(hours=2)

        expected = [datetime(2012, 1, 1, hour, 0, 0) for hour in [0, 2, 4, 6, 8, 10]]

        result = [t for t in time_utils.gen_time(s, e, i)]

        self.assertEqual(result, expected)
