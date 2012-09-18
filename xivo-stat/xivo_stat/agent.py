# -*- coding: utf-8 -*-

from xivo_stat import core
from xivo_stat import time_utils
from datetime import timedelta
import copy


class AgentLoginTimeComputer(object):

    def __init__(self, start, end, interval_size):
        self.start = start
        self.end = end
        self.interval_size = interval_size
        self.possible_intervals = list(core.gen_time(start, end, interval_size))

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
