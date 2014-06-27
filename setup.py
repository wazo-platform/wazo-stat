#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='xivo-stat',
    version='0.1',
    description='XiVO Stat Generation Script',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://git.xivo.io/',
    license='GPLv3',
    packages=['xivo_stat',
              'xivo_stat.bin'],
    scripts=['bin/xivo-stat'],
)
