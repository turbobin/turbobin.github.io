---
layout:     post
title:      Python常用的时间处理函数
subtitle:
date:       2020-03-18
author:     turbobin
header-img:
catalog: true
category: 技术
tags:
    - Python
---

在工作中经常需要用到时间处理，比如从时间类型转时间戳，从时间类型转字符串，字符转时间戳...

为此积累一下 Python 中常用的时间处理函数，后面遇到再补充。

`time_tool.py`

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import arrow    # 需要先 pip install arrow
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta    # 需要先pip install python-dateutil


def get_day_id(delta=0):
    """获取某天的day_id"""
    date = datetime.now() + timedelta(days=delta)
    day_id = int(date.strftime('%Y%m%d'))
    return day_id


def get_day_id_by_ts(ts, delta=0):
    """根据获取时间戳day_id"""
    dt = datetime.fromtimestamp(ts) + timedelta(days=delta)
    day_id = int(dt.strftime('%Y%m%d'))
    return day_id


def get_ts_by_day_id(day_id, delta=0, clock=0):
    """获取某一天(整点)的时间戳"""
    st = time.strptime(str(day_id)+str(clock), "%Y%m%d%H")
    ts = time.mktime(st) + 86400 * delta
    return int(ts)


def get_day_id_by_date(date, delta=0):
    """根据date获取day_id"""
    dt = date + timedelta(days=delta)
    day_id = int(dt.strftime('%Y%m%d'))
    return day_id


def get_date_by_day_id(day_id, delta=0, clock=0):
    """获取某一天(整点)的date"""
    st = time.strptime(str(day_id)+str(clock), "%Y%m%d%H")
    ts = time.mktime(st) + 86400 * delta
    return datetime.fromtimestamp(ts)


def get_week_id(delta=0):
    """今年的第几周"""
    date = datetime.now() + timedelta(weeks=delta)
    year, week_id, __ = date.isocalendar()
    return year, week_id


def get_week_start_day_id(delta=0):
    """一周的开始日期"""
    date = datetime.now() + timedelta(weeks=delta)
    week_begin = (date - timedelta(days=date.weekday())).strftime('%Y%m%d')
    return int(week_begin)


def get_week_end_day_id(delta=0):
    """一周结束日期"""
    date = datetime.now() + timedelta(weeks=delta)
    week_end = (date + timedelta(days=6-date.weekday())).strftime('%Y%m%d')
    return int(week_end)


def get_month_start_day_id(delta=0):
    """月开始日期"""
    now = datetime.now()
    month_start = datetime(now.year, now.month + delta, 1).strftime('%Y%m%d')
    return int(month_start)


def get_month_end_day_id(delta=0):
    """月结束日期"""
    now = datetime.now()
    month_end_date = datetime(now.year, now.month + 1 + delta, 1) - timedelta(days=1)
    return int(month_end_date.strftime('%Y%m%d'))


def get_relative_date(date, delta=0, relative_type="day"):
    """获取相对日期"""
    relative_date = date
    if relative_type == "hour":
        relative_date = date + relativedelta(hours=delta)
    elif relative_type == "day":
        relative_date = date + relativedelta(days=delta)
    elif relative_type == "week":
        relative_date = date + relativedelta(weeks=delta)
    elif relative_type == "month":
        relative_date = date + relativedelta(months=delta)
    elif relative_type == "year":
        relative_date = date + relativedelta(years=delta)
    return relative_date


def get_humanize_time(date, lg="zh"):
    """返回可读化时间"""
    a = arrow.get(date, tzinfo='local')
    return a.humanize(locale=lg)


def date_format(date, f="YYYY-MM-DD HH:mm:ss"):
    """日期格式化，可以传date对象或时间戳"""
    return arrow.get(date, tzinfo='local').format(f)


if __name__ == '__main__':
    print('1:', get_day_id(0))
    print('2:', get_day_id_by_ts(1563811200, 0))
    print('3:', get_ts_by_day_id(20200312, -1))
    print('4:', get_week_id())
    print('5:', get_week_start_day_id(0))
    print('6:', get_week_end_day_id(0))
    print('7:', get_month_start_day_id(0))
    print('8:', get_month_end_day_id(-3))
    print('9:', get_relative_date(datetime.now()))
    print('10:', get_humanize_time(time.time() - 60, "zh"))
    print('11:', date_format(time.time()))

```

返回：

```
1： 20200318
2： 20190723
3： 1583856000
4： (2020, 12)
5： 20200316
6： 20200322
7： 20200301
8： 20191231
9： 2020-03-18 18:20:16.844000
10： 1分钟前
11： 2020-03-18 18:20:16
```

