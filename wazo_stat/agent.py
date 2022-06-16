# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from datetime import timedelta

from xivo_dao import stat_dao, stat_agent_periodic_dao
from xivo_dao import queue_log_dao

from wazo_stat import time_utils

logger = logging.getLogger(__name__)

INTERVAL = timedelta(hours=1)


def _merge_update_agent_statistics(*args):
    result = {}

    for stats in args:
        for time_interval, stat in stats.items():
            if time_interval not in result:
                result[time_interval] = {}
            for agent, time_map in stat.items():
                if agent not in result[time_interval]:
                    result[time_interval][agent] = time_map
                else:
                    for time_label, time in time_map.items():
                        current_val = result[time_interval][agent].get(
                            time_label, timedelta(seconds=0)
                        )
                        result[time_interval][agent][time_label] = time + current_val

    return result


def insert_periodic_stat(dao_sess, start, end):
    time_computer = AgentTimeComputer(start, end, INTERVAL)

    login_intervals = stat_dao.get_login_intervals_in_range(dao_sess, start, end)
    pause_intervals = stat_dao.get_pause_intervals_in_range(dao_sess, start, end)

    periodic_stats_login = time_computer.compute_login_time_in_period(login_intervals)
    periodic_stats_pause = time_computer.compute_pause_time_in_period(pause_intervals)
    periodic_stats_wrapup = queue_log_dao.get_wrapup_times(
        dao_sess, start, end, INTERVAL
    )
    dao_sess.flush()

    periodic_stats = _merge_update_agent_statistics(
        periodic_stats_login,
        periodic_stats_pause,
        periodic_stats_wrapup,
    )

    for period, stats in periodic_stats.items():
        stat_agent_periodic_dao.insert_stats(dao_sess, stats, period)
    dao_sess.flush()


def remove_after_start(dao_sess, date):
    logger.info('Removing agent cache after %s', date)
    stat_agent_periodic_dao.remove_after(dao_sess, date)


class AgentTimeComputer:
    def __init__(self, start, end, interval_size):
        self.start = start
        self.end = end
        self.interval_size = interval_size
        self.possible_intervals = list(time_utils.gen_time(start, end, interval_size))

    def compute_login_time_in_period(self, sessions_by_agent):
        return self._compute_time_in_period('login_time', sessions_by_agent)

    def compute_pause_time_in_period(self, sessions_by_agent):
        return self._compute_time_in_period('pause_time', sessions_by_agent)

    def _compute_time_in_period(self, time_type, sessions_by_agent):
        results = {}

        for agent, sessions in sessions_by_agent.items():
            for time_start, time_end in sessions:
                if not time_end:
                    time_end = self.end
                touched_periods = time_utils.get_period_start_for_time_range(
                    self.possible_intervals, time_start, time_end
                )

                for period_start in touched_periods:
                    if period_start not in results:
                        results[period_start] = {}
                    period_end = period_start + self.interval_size
                    end_in_interval = min(time_end, period_end)
                    start_in_interval = max(time_start, period_start)
                    delta = end_in_interval - start_in_interval
                    self._add_time_to_agent_in_period(
                        results[period_start], agent, time_type, delta
                    )

        return results

    def _add_time_to_agent_in_period(self, period, agent, time_type, duration):
        if agent not in period:
            period[agent] = {}
        if time_type not in period[agent]:
            period[agent][time_type] = duration
        else:
            period[agent][time_type] += duration
