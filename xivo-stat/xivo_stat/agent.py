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
            results[agent] = {}
            for login_start, login_end in login_sessions:
                touched_periods = time_utils.get_period_start_for_time_range(
                    self.possible_intervals, login_start, login_end)

                self._increase_touched_periods(
                    results[agent], login_start, login_end, touched_periods)

        return results

    def _increase_touched_periods(self, agent_periods, login_start, login_end, touched_periods):
        for period_start in touched_periods:
            period_end = period_start + self.interval_size
            end_in_interval = min(login_end, period_end)
            start_in_interval = max(login_start, period_start)
            delta = copy.deepcopy(end_in_interval - start_in_interval)
            self._add_time_to_agent_in_period(
                agent_periods, period_start, delta)

    def _add_time_to_agent_in_period(self, agent_periods, period_start, duration):
        if duration == timedelta(0):
            return

        if period_start not in agent_periods:
            agent_periods[period_start] = duration
        else:
            agent_periods[period_start] += duration
