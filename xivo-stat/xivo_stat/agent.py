# -*- coding: utf-8 -*-

from datetime import timedelta

from xivo_stat import time_utils
from xivo_dao import stat_agent_periodic_dao
from xivo_dao import stat_dao


ONE_HOUR = timedelta(hours=1)


def _merge_update_agent_statistics(*args):
    result = {}

    for stats in args:
        for time_interval, stat in stats.iteritems():
            if time_interval not in result:
                result[time_interval] = {}
            for agent, time_map in stat.iteritems():
                if agent not in result[time_interval]:
                    result[time_interval][agent] = time_map
                else:
                    for time_label, time in time_map.iteritems():
                        current_val = result[time_interval][agent].get(time_label, timedelta(seconds=0))
                        result[time_interval][agent][time_label] = time + current_val

    return result


def insert_periodic_stat(start, end):
    print 'Inserting agent periodic stat'
    time_computer = AgentTimeComputer(start, end, ONE_HOUR)

    login_intervals = stat_dao.get_login_intervals_in_range(start, end)
    pause_intervals = stat_dao.get_pause_intervals_in_range(start, end)

    periodic_stats_login = time_computer.compute_login_time_in_period(login_intervals)
    periodic_stats_pause = time_computer.compute_pause_time_in_period(pause_intervals)

    periodic_stats = _merge_update_agent_statistics(periodic_stats_login, periodic_stats_pause)

    for period, stats in periodic_stats.iteritems():
        stat_agent_periodic_dao.insert_stats(stats, period)


def remove_after_start(date):
    print 'Removing agent cache after', date
    stat_agent_periodic_dao.remove_after(date)


class AgentTimeComputer(object):

    def __init__(self, start, end, interval_size):
        self.start = start
        self.end = end
        self.interval_size = interval_size
        self.possible_intervals = list(time_utils.gen_time(start, end, interval_size))

    def compute_login_time_in_period(self, sessions_by_agent):
        return self._compute_time_in_period('login_time', sessions_by_agent)

    def compute_pause_time_in_period(self, sessions_by_agent):
        return self._compute_time_in_period('pause_time', sessions_by_agent)

    def _compute_time_in_period(self, type, sessions_by_agent):
        results = {}

        for agent, sessions in sessions_by_agent.iteritems():
            for time_start, time_end in sessions:
                touched_periods = time_utils.get_period_start_for_time_range(
                    self.possible_intervals, time_start, time_end)

                for period_start in touched_periods:
                    if period_start not in results:
                        results[period_start] = {}
                    period_end = period_start + self.interval_size
                    end_in_interval = min(time_end, period_end)
                    start_in_interval = max(time_start, period_start)
                    delta = end_in_interval - start_in_interval
                    self._add_time_to_agent_in_period(
                        results[period_start], agent, type, delta)

        return results

    def _add_time_to_agent_in_period(self, period, agent, time_type, duration):
        if agent not in period:
            period[agent] = {}
        if time_type not in period[agent]:
            period[agent][time_type] = duration
        else:
            period[agent][time_type] += duration
