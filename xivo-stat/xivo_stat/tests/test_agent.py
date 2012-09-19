# -*- coding: utf-8 -*-

import unittest

from mock import Mock, patch

from datetime import datetime as dt
from datetime import timedelta

from xivo_stat import agent


ONE_HOUR = timedelta(hours=1)


mock_get_login_intervals_in_range = Mock()
mock_insert_stats = Mock()


mocks = [mock_get_login_intervals_in_range,
         mock_insert_stats]


class TestAgent(unittest.TestCase):

    def setUp(self):
        map(lambda mock: mock.reset_mock(), mocks)

    @patch('xivo_dao.stat_agent_periodic_dao.insert_stats',
           mock_insert_stats)
    @patch('xivo_dao.stat_dao.get_login_intervals_in_range',
           mock_get_login_intervals_in_range)
    def test_insert_periodic_stat(self):
        agent_id_1 = 12
        agent_id_2 = 13
        input_stats = {
            agent_id_1: [
                (dt(2012, 01, 01, 01, 05, 00), dt(2012, 01, 01, 01, 15, 00)),
                (dt(2012, 01, 01, 01, 20, 00), dt(2012, 01, 01, 02, 20, 00)),
                ],
            agent_id_2: [
                (dt(2012, 01, 01, 01, 00, 00), dt(2012, 01, 01, 05, 00, 00)),
                ]
            }
        output_stats = {
            dt(2012, 01, 01, 01, 00, 00): {
                agent_id_1: timedelta(minutes=50),
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 02, 00, 00): {
                agent_id_1: timedelta(minutes=20),
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 03, 00, 00): {
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 04, 00, 00): {
                agent_id_2: ONE_HOUR,
                }
            }
        start = dt(2012, 01, 01, 01, 00, 00)
        end = dt(2012, 01, 01, 04, 00, 00)

        mock_get_login_intervals_in_range.return_value = input_stats
        login_time_computer = Mock(agent.AgentLoginTimeComputer)
        login_time_computer.compute_login_time_in_period.return_value = output_stats

        agent.insert_periodic_stat(start, end)

        for period_start, agents_stats in output_stats.iteritems():
            mock_insert_stats.assert_any_calls(
                agents_stats, period_start)


class TestAgentLoginTimeComputer(unittest.TestCase):

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
            dt(2012, 01, 01, 01, 00, 00): {
                agent_id_1: timedelta(minutes=50),
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 02, 00, 00): {
                agent_id_1: timedelta(minutes=20),
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 03, 00, 00): {
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 04, 00, 00): {
                agent_id_2: ONE_HOUR,
                }
            }

        computer = agent.AgentLoginTimeComputer(
            start,
            end,
            interval_size,
            )

        result = computer.compute_login_time_in_period(logins)

        self.assertEqual(result, expected)

    def test_compute_login_time_in_period_double_logins(self):
        agent_id_1 = 1
        agent_id_2 = 2

        start = dt(2012, 1, 1)
        end = dt(2012, 1, 1, 23, 59, 59, 999999)

        logins = {
            agent_id_1: [
                (dt(2012, 01, 01, 01, 00, 00), dt(2012, 01, 01, 02, 00, 00)),
                (dt(2012, 01, 01, 01, 05, 00), dt(2012, 01, 01, 01, 15, 00)),
                (dt(2012, 01, 01, 01, 20, 00), dt(2012, 01, 01, 02, 20, 00)),
                ],
            agent_id_2: [
                (dt(2012, 01, 01, 01, 00, 00), dt(2012, 01, 01, 05, 00, 00)),
                ]
            }

        interval_size = ONE_HOUR

        expected = {
            dt(2012, 01, 01, 01, 00, 00): {
                agent_id_1: ONE_HOUR,
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 02, 00, 00): {
                agent_id_1: timedelta(minutes=20),
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 03, 00, 00): {
                agent_id_2: ONE_HOUR,
                },
            dt(2012, 01, 01, 04, 00, 00): {
                agent_id_2: ONE_HOUR,
                }
            }

        computer = agent.AgentLoginTimeComputer(
            start,
            end,
            interval_size,
            )

        result = computer.compute_login_time_in_period(logins)

        from pprint import pprint
        pprint(result)

        self.assertEqual(result, expected)
