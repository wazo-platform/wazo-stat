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

def get_period_start_for_time_range(time_list, start, end):
    smaller = None
    bigger = None

    for i, t in enumerate(time_list):
        if t <= start:
            smaller = i
        if t >= end and not bigger:
            bigger = i

    return time_list[smaller:bigger]


def gen_time(start, end, step):
    tmp = start
    while tmp <= end:
        yield tmp
        tmp += step
