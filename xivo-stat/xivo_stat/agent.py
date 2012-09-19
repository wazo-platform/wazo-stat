# -*- coding: utf-8 -*-

from datetime import timedelta

from xivo_stat import time_utils
from xivo_dao import stat_agent_periodic_dao
from xivo_dao import stat_dao


ONE_HOUR = timedelta(hours=1)


def insert_periodic_stat(start, end):
    print 'Inserting agent periodic stat'
    login_intervals = stat_dao.get_login_intervals_in_range(start, end)
    login_computer = AgentLoginTimeComputer(start, end, ONE_HOUR)
    periodic_stats = login_computer.compute_login_time_in_period(login_intervals)
    for period, stats in periodic_stats.iteritems():
        stat_agent_periodic_dao.insert_stats(stats, period)


class AgentLoginTimeComputer(object):

    def __init__(self, start, end, interval_size):
        self.start = start
        self.end = end
        self.interval_size = interval_size
        self.possible_intervals = list(time_utils.gen_time(start, end, interval_size))

    def compute_login_time_in_period(self, login_sessions_by_agent):
        results = {}

        for agent, login_sessions in login_sessions_by_agent.iteritems():
            for login_start, login_end in login_sessions:
                touched_periods = time_utils.get_period_start_for_time_range(
                    self.possible_intervals, login_start, login_end)

                for period_start in touched_periods:
                    if period_start not in results:
                        results[period_start] = {}
                    period_end = period_start + self.interval_size
                    end_in_interval = min(login_end, period_end)
                    start_in_interval = max(login_start, period_start)
                    delta = end_in_interval - start_in_interval
                    self._add_time_to_agent_in_period(
                        results[period_start], agent, delta)

        return results

    def _add_time_to_agent_in_period(self, period, agent, duration):
        if duration == timedelta(0):
            return

        if agent not in period:
            period[agent] = duration
        else:
            period[agent] += duration

        period[agent] = self._ignore_multiple_logins(period[agent])

    def _ignore_multiple_logins(self, login_time):
        """
        Work around an historical bug in chan_agent.so where you could login multiple times
        Fixed in XiVO 12.18
        """
        return min(login_time, ONE_HOUR)
