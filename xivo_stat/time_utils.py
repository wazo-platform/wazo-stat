# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later


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
