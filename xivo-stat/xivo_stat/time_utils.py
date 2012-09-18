# -*- coding: utf-8 -*-


def get_period_start_for_time_range(time_list, start, end):
    smaller = None
    bigger = None

    for i, t in enumerate(time_list):
        if t < start:
            smaller = i
        if t > end and not bigger:
            bigger = i

    return time_list[smaller:bigger]
