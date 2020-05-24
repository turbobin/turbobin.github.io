---
layout:     post
title:      Redis内存分析与清理
subtitle:
date:       2020-05-18
author:     turbobin
header-img:
catalog: true
category: 工具
tags:
    - redis
---



最近 redis 的内存告警，需要对 redis 内存进行一次清理，要清理就要先进行 redis 的内存分析，看有哪些比较大的 key 占用。

由于我们用的腾讯云上的 redis，每天会备份一个 rdb 文件，我们使用内网把 rdb 文件下载下来。

网上搜索之后，决定采用这个工具：[https://github.com/xueqiu/rdr](https://github.com/xueqiu/rdr) ，可视化界面很漂亮，展示了 top key 和 前缀 key 的统计信息。具体介绍可以查看这片文章：[如果优雅的分析redis里存了啥？](https://www.infoq.cn/article/analysis-redis)

key 的导出使用到了比较知名的 [redis-rdb-tools](https://github.com/sripathikrishnan/redis-rdb-tools) 工具。

下面记录具体步骤。

### 导出 redis rdb 文件

- 登陆腾讯云，查看 redis 实例的备份与恢复，可以看到每天的备份记录和下载链接。复制需要分析的 redis 最新备份的 rdb 文件的内网下载地址。

- 在开发机上新建一个 `url.txt` 文件，粘贴下载地址，格式为：URL  filename，如果下载多个 rdb，则一行写一个，其中 filename 为下载后重命名的文件名。如：

  ```
  # url.txt
  https://redis-database-backup-ap-guangzhou-1256375829.cos.ap-guangzhou.myqcloud.com/1251025769/redis/80002330/data/2020-04-13/8188127-2466249-80002330.rdb?q-sign-algorithm=sha1&q-ak=AKID2ymQxUC22pR7gD5v6A3lIdlm12wfQbmp&q-sign-time=1586776810;1586798470&q-key-time=1586776810;1586798470&q-header-list=&q-url-param-list=&q-signature=61868f66c7f68febb34eb610241cacdd1a14311d    topic_redis.rdb
  ```

- 建一个 `download.sh`  下载脚本，把 rdb 文件下载到本地：`sh download.sh`

  ```bash
  #!/bin/bash
  
  while read url filename; do
      echo "downloading $filename..."
      wget -c $url -O $filename
  done < urls.txt
  ```

- 把 `rdr`工具下载下来，添加执行权限：`chmod a+x ./rdr*`，然后启动 rdb 可视化分析：`./rdr show -p 8005 *.rdb`，启动需要等待几分钟。如果文件比较大，启动时会占用大量内存，如果机器内存不足，指定某个具体的 rdb 文件，不要一次性分析多个rdb 文件。

- 浏览器访问本机的 8005 端口。

### 分析 key

- 导出某个占用比较大的相同前缀的 key（需要先安装 redis-rdb-tools 工具）：

  `rdb --command justkeys --key "yd_en*" user_redis_node0.rdb > yd_en_keys.txt`。如果导出需要包含数据，把 `justkeys` 改成 `justkeyvals`

- 去重：`sort yd_en_keys.txt | uniq > yd_en_keys_uniq.txt`

### 清理 key

使用 python 脚本来进行清理：

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

sys.path.append("/data2/wwwroot/apps/sport_caochaobin")

from ydredis import common_redis
import time
import common


class Handle(object):
    def __init__(self):
        self.redis_topic = common_redis.redis_topic()	# python redis客户端

    def delete_redis_expire_key(self, filename, prefix):
        print "============== opend {} ==========".format(filename)
        # 使用 redis pipeline 操作
        pipe = self.redis_topic.pipeline(transaction=False)
        index = 0
        count = 0
        with open(filename, 'r') as f:
            for line in f:
                if key.startswith(prefix):
                    index += 1
                    pipe.delete(key)
                    print "{}. '{}'  has been killed!".format(index, key)
                    # 每遍历 1000 条执行一次，停顿 1s
                    if index % 1000 == 0:
                        ret = pipe.execute()
                        print "ret:", ret
                        time.sleep(1)
        pipe.execute()


if __name__ == "__main__":
    handle = Handle()
    filename = "./yd_en_keys_uniq.txt"
    prefix = "yd_en_2019"
    handle.delete_redis_expire_key(filename, prefix)
```