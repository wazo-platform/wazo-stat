# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest

from datetime import datetime
from datetime import timedelta

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

    def test_gen_time(self):
        s = datetime(2012, 1, 1)
        e = datetime(2012, 1, 1, 11, 59, 59)
        i = timedelta(hours=2)

        expected = [datetime(2012, 1, 1, hour, 0, 0)
                    for hour in [0, 2, 4, 6, 8, 10]]

        result = [t for t in time_utils.gen_time(s, e, i)]

        self.assertEqual(result, expected)
