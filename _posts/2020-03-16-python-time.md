---
layout:     post
title:      Python常用的时间处理函数
subtitle:   
date:       2020-03-16
author:     turbobin
header-img: 
catalog: true
category: 技术
tags: Python
    - 
---

在工作中经常需要用到时间处理，比如从时间类型转时间戳，从时间类型转字符串，字符转时间戳...

为此积累一下 Python 中常用的时间处理函数，后面遇到再补充。

`time_tool.py`

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta


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


if __name__ == '__main__':
    print get_day_id(0)
    print get_day_id_by_ts(1563811200, 0)
    print get_ts_by_day_id(20200312, -1)
    print get_week_id()
    print get_week_start_day_id(0)
    print get_week_end_day_id(0)
    print get_month_start_day_id(0)
    print get_month_end_day_id(-3)
```

另外还有一些不错的时间处理模块 , 如`pytho-dateutil`，`arrow`

arrow 简要教程链接：https://foofish.net/python-arrow.html