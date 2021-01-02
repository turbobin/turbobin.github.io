---
layout:     post
title:      使用Python装饰器构造一个LRU本地缓存
subtitle:   
date:       2020-12-30
author:     turbobin
catalog: true
category: 技术
tags:

   - [Python, LRU]
---

本地缓存指的是在代码运行中动态分配的内存，一般存在于当前进程地址空间的堆内存中，如果不人为的显式释放，将会一直存在进程中。本地缓存和 Memcached 或 Redis 这样的远程缓存区别是，本地缓存有更高的执行效率，没有网络传输的消耗，缺点是没有自动过期的机制，存放的数据量也有限。

本地缓存可以显著提高代码的执行效率，比如，看下面这样一段代码：

```python
def get_user_info(user_id):
    """查询用户信息"""
    sql = "select * from user_info where user_id={user_id}".format(user_id=user_id)
    user_info = db.query(sql)
    return user_info
```

如果这个函数被频繁调用（比如放在循环中），每次都需要去查询数据库，效率必然很低，那么可以使用本地缓存来优化：

```python
def get_user_info(user_id, cache={}):
    """查询用户信息"""
    if user_id in cache:
        # 先查询本地缓存
        return cache[user_id]
    sql = "select * from user_info where user_id={user_id}".format(user_id=user_id)
    user_info = db.query(sql)
    cache[user_id] = user_info
    return user_info
```

这样，已经查询过一次的用户信息将会存在于本地缓存 cache 中，而不用每次去数据库查询。不过，这样的本地缓存有两个缺点：

- 如果不重启服务，缓存将会一直存在于进程地址空间中，永不过期。如果在其他地方更新了用户信息，那么本地缓存中取到的将一直是旧的数据。
- 缓存大小没有限制。假设有 100 w 个用户获取了用户信息，那么 cache 中将会缓存 100w 个用户信息，直接就导致内存泄露了，进程有可能被 OOM(Out Of Memery) 杀死。

为了解决这两个问题，我们来构造一个专门用于本地缓存的 Python 装饰器，提供两个功能：

- 支持缓存数据过期
- 内存大小有限制，超过后使用 LRU 缓存淘汰算法对缓存数据进行清理

具体实现看如下代码：

缓存工具类 `mycache.py`

```python
# mycache.py
import time
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.cache = OrderedDict()

    def set(self, key, value):
        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        if key in self.cache:
            self.cache.pop(key)
        self.cache[key] = value

    def get(self, key):
        if key not in self.cache:
            return None
        value = self.cache[key]
        self.cache.pop(key)
        self.cache[key] = value
        return value

    def pop(self, key):
        self.cache.pop(key)
        
        
class Cache:
    native_cache = LRUCache()
    
    @staticmethod
    def getNativeCache(key, expire_ts=300):
        info = Cache.native_cache.get(key)
        if info is not None:
            ts = info["ts"]
            diff_ts = int(time.time()) - ts
            if diff_ts > expire_ts:
                # 过期失效
                Cache.native_cache.pop(key)
                return None
            return info["value"]
        return None

    @staticmethod
    def setNativeCache(key, value):
        info = dict(value=value, ts=int(time.time()))
        Cache.native_cache.set(key, info)
```

在公共模块 `common.py` 中写一个装饰器

```python
# common.py
import mycache

def native_cache(business_type, expire_ts=300):
    """
    装饰器本地缓存,目前只支持*args参数
    """
    def decorator(func):
        def wrapper(*args):
            key = business_type + "_" + "_".join(map(str, args))
            value = mycache.Cache.getNativeCache(key, expire_ts)
            if value is None:
                value = func(*args)
                mycache.Cache.setNativeCache(key, value)
            return value
        return wrapper
    return decorator
```

构造完成，用法如下：

```python
import common

@common.native_cache("user_info", expire_ts=300)
def get_user_info(user_id):
    """查询用户信息"""
    sql = "select * from user_info where user_id={user_id}".format(user_id=user_id)
    user_info = db.query(sql)
    return user_info
```

