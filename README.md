# wazo-stat
[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-stat)](https://jenkins.wazo.community/job/wazo-stat)

Wazo statistic generation utilities

## Running unit tests

```shell
apt-get install libpq-dev python3-dev libyaml-dev
pip install tox
tox --recreate -e py311
```
