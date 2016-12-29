#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-stat',
    version='0.1',
    description='XiVO Stat Generation Script',
    author='Wazo Authors',
    author_email='dev.wazo@gmail.com',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),
    scripts=['bin/xivo-stat'],
)
