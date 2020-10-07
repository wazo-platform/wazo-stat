#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-stat',
    version='0.1',
    description='Wazo Stat Generation Script',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='https://wazo-platform.org',
    license='GPLv3',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'xivo-stat=xivo_stat.main:main',
        ]
    }
)
