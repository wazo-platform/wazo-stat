# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from datetime import datetime as dt
from datetime import timedelta

from mock import ANY
from mock import Mock
from mock import patch
from xivo_dao.helpers.db_manager import daosession

from xivo_stat import agent

ONE_HOUR = timedelta(hours=1)


@daosession
def _session(session):
    return session


class TestAgent(unittest.TestCase):

    @patch('xivo_dao.stat_agent_periodic_dao.insert_stats')
    @patch('xivo_dao.stat_dao.get_login_intervals_in_range')
    @patch('xivo_dao.stat_dao.get_pause_intervals_in_range')
    @patch('xivo_dao.queue_log_dao.get_wrapup_times')
    def test_insert_periodic_stat(self,
                                  mock_get_wrapup_times,
                                  mock_get_pause_intervals_in_range,
                                  mock_get_login_intervals_in_range,
                                  mock_insert_stats):
        agent_id_1 = 12
        agent_id_2 = 13
        login = {
            agent_id_1: [
                (dt(2012, 1, 1, 1, 5), dt(2012, 1, 1, 1, 15)),
                (dt(2012, 1, 1, 1, 20), dt(2012, 1, 1, 2, 20)),
            ],
            agent_id_2: [
                (dt(2012, 1, 1, 1), dt(2012, 1, 1, 5)),
            ]
        }
        pause = {
            agent_id_1: [
                (dt(2012, 1, 1, 1, 35), dt(2012, 1, 1, 1, 40)),
            ],
            agent_id_2: [
                (dt(2012, 1, 1, 2), dt(2012, 1, 1, 3)),
            ]
        }
        output_stats = {
            dt(2012, 1, 1, 1): {
                agent_id_1: {'login_time': timedelta(minutes=50),
                             'pause_time': timedelta(minutes=5)},
                agent_id_2: {'login_time': ONE_HOUR},
            },
            dt(2012, 1, 1, 2): {
                agent_id_1: {'login_time': timedelta(minutes=20)},
                agent_id_2: {'login_time': ONE_HOUR,
                             'pause_time': ONE_HOUR},
            },
            dt(2012, 1, 1, 3): {
                agent_id_1: {'wrapup_time': timedelta(seconds=15)},
                agent_id_2: {'login_time': ONE_HOUR},
            },
            dt(2012, 1, 1, 4): {
                agent_id_2: {'login_time': ONE_HOUR},
            }
        }
        wrapups = {
            dt(2012, 1, 1, 3): {
                agent_id_1: {'wrapup_time': timedelta(seconds=15)}
            },
        }
        start = dt(2012, 1, 1, 1)
        end = dt(2012, 1, 1, 4)

        mock_get_login_intervals_in_range.return_value = login
        mock_get_pause_intervals_in_range.return_value = pause
        mock_get_wrapup_times.return_value = wrapups
        time_computer = Mock(agent.AgentTimeComputer)
        time_computer.compute_login_time_in_period.return_value = output_stats
        time_computer.compute_pause_time_in_period.return_value = output_stats

        agent.insert_periodic_stat(_session(), start, end)

        for period_start, agents_stats in output_stats.iteritems():
            mock_insert_stats.assert_any_call(ANY, agents_stats, period_start)


class TestAgentLoginTimeComputer(unittest.TestCase):

    def test__add_time_to_agent_in_period(self):
        start = dt(2012, 1, 1)
        end = dt(2012, 1, 1, 23, 59, 59, 999999)
        interval_size = ONE_HOUR

        period = {
            dt(2012, 1, 1, 1): {}
        }
        agent_id = 1
        time_type = 'pause_time'
        duration = timedelta(minutes=10)

        computer = agent.AgentTimeComputer(
            start,
            end,
            interval_size,
        )

        expected_result = {
            dt(2012, 1, 1, 1): {1: {'pause_time': duration}}
        }

        computer._add_time_to_agent_in_period(period[dt(2012, 1, 1, 1)], agent_id, time_type, duration)

        self.assertEqual(period, expected_result)

    def test_merge_update_agent_statistics(self):
        agent_id_1, agent_id_2 = 12, 23
        stat1 = {
            dt(2012, 1, 1, 1): {agent_id_1: {'login_time': timedelta(minutes=50)},
                                agent_id_2: {'login_time': ONE_HOUR}},
            dt(2012, 1, 1, 2): {agent_id_1: {'login_time': timedelta(minutes=20)},
                                agent_id_2: {'login_time': ONE_HOUR}},
            dt(2012, 1, 1, 3): {agent_id_2: {'login_time': ONE_HOUR}},
            dt(2012, 1, 1, 4): {agent_id_2: {'login_time': ONE_HOUR}}
        }

        stat2 = {
            dt(2012, 1, 1, 1): {
                agent_id_1: {'pause_time': timedelta(minutes=13)},
                agent_id_2: {'pause_time': timedelta(minutes=13)},
            },
            dt(2012, 1, 1, 2): {
                agent_id_1: {'pause_time': timedelta(minutes=33)},
                agent_id_2: {'pause_time': timedelta(minutes=13)},
            },
            dt(2012, 1, 1, 3): {
                agent_id_2: {'pause_time': ONE_HOUR},
            },
            dt(2012, 1, 1, 4): {
                agent_id_2: {'pause_time': ONE_HOUR},
            }
        }

        expected = {
            dt(2012, 1, 1, 1): {
                agent_id_1: {'login_time': timedelta(minutes=50),
                             'pause_time': timedelta(minutes=13)},
                agent_id_2: {'login_time': ONE_HOUR,
                             'pause_time': timedelta(minutes=13)},
            },
            dt(2012, 1, 1, 2): {
                agent_id_1: {'login_time': timedelta(minutes=20),
                             'pause_time': timedelta(minutes=33)},
                agent_id_2: {'login_time': ONE_HOUR,
                             'pause_time': timedelta(minutes=13)},
            },
            dt(2012, 1, 1, 3): {
                agent_id_2: {'login_time': ONE_HOUR,
                             'pause_time': ONE_HOUR},
            },
            dt(2012, 1, 1, 4): {
                agent_id_2: {'login_time': ONE_HOUR,
                             'pause_time': ONE_HOUR},
            }
        }

        result = agent._merge_update_agent_statistics(stat1, stat2)

        self.assertEqual(result, expected)

    def test_compute_time_in_period(self):
        agent_id_1 = 1
        agent_id_2 = 2

        computer = agent.AgentTimeComputer(
            dt(2012, 1, 1),
            dt(2012, 1, 1, 23, 59, 59, 999999),
            ONE_HOUR,
        )

        logins = {
            agent_id_1: [
                (dt(2012, 1, 1, 1, 5), dt(2012, 1, 1, 1, 15)),
                (dt(2012, 1, 1, 1, 20), dt(2012, 1, 1, 2, 20)),
            ],
            agent_id_2: [
                (dt(2012, 1, 1, 1), dt(2012, 1, 1, 5)),
            ]
        }

        expected = {
            dt(2012, 1, 1, 1): {
                agent_id_1: {'login_time': timedelta(minutes=50)},
                agent_id_2: {'login_time': ONE_HOUR}
            },
            dt(2012, 1, 1, 2): {
                agent_id_1: {'login_time': timedelta(minutes=20)},
                agent_id_2: {'login_time': ONE_HOUR}
            },
            dt(2012, 1, 1, 3): {
                agent_id_2: {'login_time': ONE_HOUR}
            },
            dt(2012, 1, 1, 4): {
                agent_id_2: {'login_time': ONE_HOUR}
            }
        }

        result = computer._compute_time_in_period('login_time', logins)

        self.assertEqual(result, expected)

    @patch('xivo_dao.stat_agent_periodic_dao.remove_after')
    def test_remove_after_start(self, mock_stat_agent_periodic_remove_after):
        s = dt(2012, 1, 1)

        agent.remove_after_start(_session(), s)

        mock_stat_agent_periodic_remove_after.assert_called_once_with(_session(), s)
