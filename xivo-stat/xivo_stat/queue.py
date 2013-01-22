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

from xivo_dao import queue_log_dao
from xivo_dao import stat_dao
from xivo_dao import stat_call_on_queue_dao
from xivo_dao import stat_queue_periodic_dao


def fill_abandoned_call(start, end):
    abandoned_calls = queue_log_dao.get_queue_abandoned_call(start, end)
    for call in abandoned_calls:
        stat_call_on_queue_dao.add_abandoned_call(call['callid'],
                                                  call['time'],
                                                  call['queue_name'],
                                                  call['waittime'])


def fill_timeout_call(start, end):
    timeout_calls = queue_log_dao.get_queue_timeout_call(start, end)
    for call in timeout_calls:
        stat_call_on_queue_dao.add_timeout_call(call['callid'],
                                                call['time'],
                                                call['queue_name'],
                                                call['waittime'])


def fill_calls(start, end):
    fill_abandoned_call(start, end)
    fill_timeout_call(start, end)


def fill_simple_calls(start, end):
    print 'Inserting simple calls...'
    stat_dao.fill_simple_calls(start, end)
    print 'Inserting answered calls...'
    stat_dao.fill_answered_calls(start, end)
    print 'Inserting leaveempty calls...'
    stat_dao.fill_leaveempty_calls(start, end)


def insert_periodic_stat(start, end):
    periodic_stats = stat_call_on_queue_dao.get_periodic_stats(start, end)
    for period, stats in periodic_stats.iteritems():
        print 'Inserting queue periodic stat', period
        stat_queue_periodic_dao.insert_stats(stats, period)


def remove_after_start(date):
    print 'Removing queue cache after', date
    stat_call_on_queue_dao.remove_after(date)
    stat_queue_periodic_dao.remove_after(date)
