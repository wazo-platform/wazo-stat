# -*- coding: utf-8 -*-

import unittest
import datetime

from datetime import datetime as dt
from datetime import timedelta

from xivo_stat.agent import AgentLoginTimeComputer

ONE_HOUR = timedelta(hours=1)


class TestAgent(unittest.TestCase):

    def test_compute_login_time_in_period(self):
        agent_id_1 = 1
        agent_id_2 = 2

        start = dt(2012, 1, 1)
        end = dt(2012, 1, 1, 23, 59, 59, 999999)

        logins = {
            agent_id_1: [
                (dt(2012, 01, 01, 01, 05, 00), dt(2012, 01, 01, 01, 15, 00)),
                (dt(2012, 01, 01, 01, 20, 00), dt(2012, 01, 01, 02, 20, 00)),
                ],
            agent_id_2: [
                (dt(2012, 01, 01, 01, 00, 00), dt(2012, 01, 01, 05, 00, 00)),
                ]
            }

        interval_size = ONE_HOUR

        expected = {
            agent_id_1: {
                dt(2012, 01, 01, 01, 00, 00): timedelta(minutes=50),
                dt(2012, 01, 01, 02, 00, 00): timedelta(minutes=20),
                },
            agent_id_2: {
                dt(2012, 01, 01, 01, 00, 00): ONE_HOUR,
                dt(2012, 01, 01, 02, 00, 00): ONE_HOUR,
                dt(2012, 01, 01, 03, 00, 00): ONE_HOUR,
                dt(2012, 01, 01, 04, 00, 00): ONE_HOUR,
                }
            }

        computer = AgentLoginTimeComputer(
            start,
            end,
            interval_size,
            )

        result = computer.compute_login_time_in_period(logins)

        self.assertEqual(result, expected)
