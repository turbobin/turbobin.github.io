---
layout:     post
title:      Nginx学习笔记-系统层性能优化
subtitle:
date:       2020-05-17
author:     turbobin
header-img:
catalog: true
category: 技术
tags:
    - nginx
---

### 性能优化方法论

1、从软件层面提升硬件使用效率

- 增大 CPU 的利用率
- 增大内存的利用率
- 增大磁盘IO的利用率
- 增大网络带宽的利用率

2、提升硬件规格

- 网卡：万兆网卡，例如 10G、25G、40G等
- 磁盘：固态硬盘，关注 IOPS 和 BPS 指标
- CPU：更快的主频，更多的核心，更大的缓存，更优的架构
- 内存：更快的访问速度

3、超出硬件性能上限后使用 DNS（实用集群）

### 如何高效实用 CPU

#### 增大 Nginx 使用CPU 的有效时长

**能够使用全部CPU资源**

- master-worker 多进程架构
- worker 进程数量应该大于等于 CPU 核数

**Nginx 进程间不做无用功浪费CPU资源**

- worker 进程不应在繁忙期间主动让出 CPU
  - worker 进程间不应由于争抢造成资源耗散（worker 进程数量应当等于CPU核数）
  - worker 进程不应调用一些 API 导致主动让出 CPU（拒绝类似的第三方模块）

**不被其他进程争抢资源**

- 提升优先级占用CPU更长的时间
- 减少操作系统上耗资源的非 Nginx 进程

**设置 worker 进程数量**

```nginx
Syntax: worker_processes number | auto;		# auto 表示等于CPU核数
Default: worker_processes 1;
Context: main
```

#### 为何一个CPU可以同时运行多个进程

**宏观上并行，微观上串行**

- 操作系统把进程的运行时间分为一段段的时间片
- OS 调度系统依次选择每个进程，最多执行时间片指定的时长

**阻塞 API 引发的时间片内主动出让CPU**

- 速度不一致引发的阻塞 API（硬件执行速度不一致，例如 CPU 和磁盘）
- 业务场景产生的阻塞 API（例如同步读取网络报文）

#### 确保进程在运行态

- R 状态：正在运行或在运行队列中等待（使用 top 或 ps 命令 可以看到进程的状态）
- S 状态：休眠中，受阻，在等待 某个条件的形成或接受到信号。
- D 不可中断：收到信号不唤醒和不可运行，进程必须等待直到有中断发送
- Z 僵死：进程已终止，但进程描述符存在，直到父进程调用 wait4() 系统调用后释放
- T 停止：进程收到 SIGSTOP，SIGSTP，SIGTIN，SIGTO信号后停止运行。

#### 减少进程间切换

**使 Nginx 尽可能的处于 R 状态**

- R 状态的进程数量大于cpu核心数时，负载急速升高。

**尽可能的减少进程间切换**

- 进程切换是指 CPU 从一个进程或线程切换到另一个进程或线程。类别有主动切换（进程阻塞）和被动切换（时间片耗尽）。进程切换的耗时一般 < 5us
-  减少主动切换
- 减少被动切换（增大进程优先级）

**绑定 CPU**

#### 延迟处理新连接

使用  TCP_DEFER_ACCEPT  延迟处理新连接

```nginx
Syntax: listen address[:port][deferred];
Deafult: listen *:80 | *:8000;
Context: server
```

#### 查看上下文切换次数

- vmstat 命令

  ![image-20200510131140845](https://github.com/turbobin-cao/images/raw/main/image-20200510131140845.png)

- dstat （需要 yum install dstat）

  ![image-20200510131029662](https://github.com/turbobin-cao/images/raw/main/image-20200510131029662.png)

- pidstat -w

  ![image-20200510130548142](https://github.com/turbobin-cao/images/raw/main/image-20200510130548142.png)

  ![image-20200510131557737](https://github.com/turbobin-cao/images/raw/main/image-20200510131557737.png)

**什么决定 CPU 时间片的大小**

- Nice 静态优先级：-20 ~ 19
- Priority 动态优先级：0 ~ 139

![image-20200510132144253](https://github.com/turbobin-cao/images/raw/main/image-20200510132144253.png)

#### 设置 worker 进程的静态优先级

```nginx
Syntax: worker_priority number;		# 一般设为 -20
Default: worker_priority 0;
Contex: main
```

#### 绑定 worker 到指定 CPU

```nginx
Syntax: worker_cpu_affinity cpumask ...;
	    worker_cpu_affinity auto [cpumask];
Default: - ;
Contex: main
```

### 建立 TCP 连接的优化

**TCP 连接过程**

![image-20200510142057075](https://github.com/turbobin-cao/images/raw/main/image-20200510142057075.png)

**SYN_SENT 状态**

- net.ipv4.tcp_syn_retries=6	(主动建立连接时，发 SYN 的重试次数)
- net.ipv4.ip_local_port_range= 32768  60999    (建立连接时的本地可用端口范围)	

**主动建立连接时应用层超时时间**

- Syntax：proxy_connect_timeout time;
- Default：proxy_connect_timeout 60s;
- Context: http, stream, server, location

**SYN_RCVD 状态**

- net.ipv4.tcp_max_syn_backlog   (SYN_RCVD 状态连接的最大个数)
- net.ipv4.tcp_synack_retries     (被动建立连接时，发 SYN / ACK 的重试次数)

**服务端处理三次握手**

![image-20200510143211699](https://github.com/turbobin-cao/images/raw/main/image-20200510143211699.png)

**SYN 攻击**

攻击者短时间内伪造不同的 ip 地址的 SYN 报文，快速占满 backlog 队列，使服务不能为正常用户服务

- net.core.netdev_max_backlog  	(接收自网卡、但未被内核协议栈处理的报文队列长度)
- net.ipv4.tcp_max_syn_backlog     (SYN_RCVD  状态里连接的最大个数)
- net.ipv4.tcp_abort_on_overflow   (超过处理能力时，对新来的 SYN 直接回包 RST，丢弃连接)

**一切皆文件：句柄文件数的上限**

- 操作系统全局

  - fs.file-max：操作系统可使用的最大文件句柄数
  - 使用 fs.file-nr 可以查看当前已分配、正使用、上限

- 限制用户 `cat /etc/security/limits.conf`

  ```
  root soft nofile 65535
  root hard nofile 65535
  ```

- 限制进程 `worker_rlimit_nofile number;`

- 设置 worker 进程最大连接数量 `worker_connections number;`默认为 512。限制了包括 Nginx 与上游、下游间的连接。

**两个对列的长度**

- SYN 队列未完成握手：net.ipv4.tcp_max_syn_backlog=262144
- ACCEPT 队列已完成握手
  - net.core.somaxconn (系统级最大 backlog 队列长度)

```nginx
listen address [:port][backlog=number];
```

**TCP Fast Open**

`net.ipv4.tcp_fastopen`	(系统开启 TFO 功能)

- 0：关闭
- 1：作为客户端时可以使用 TFO
- 2：作为服务器时可以使用 TFO
- 3：无论作为客户端还是服务器，都可以使用 TFO

```nginx
listen address [:port][fastopen=number];
```

`fastopen=number`  (为防止带数据的 SYN 攻击，限制最大长度，指定 TFO 连接队列的最大长度)

### TCP 的 Keep-Alive 功能

**应用场景**

- 检测实际断掉的连接
- 用于维持与客户端间的防火墙有活跃网络包

**Linux 的 TCP keepalive**

- 发送心跳周期：`net.ipv4.tcp_keepalive_timeout = 7200`，默认7200 s
- 探测包发送间隔：`net.ipv4.tcp_keepalive_intvl = 75`
- 探测包重试次数：`net.ipv4.tcp_keepalive_probes = 9`

**Nginx 的 tcp keepalive**

- `so_keepalive=30m::10`，值分别对应 keepidle、keepintvl、keepcnt

### TCP 的 time_wait 状态

**主动关闭连接端的状态**

- fin_wait1 状态
  - net.ipv4.tcp_orphan_retries = 0，发送 FIN 报文的重试次数， 0 相当于 8
- fin_wait2 状态
  - net.ipv4.tcp_fin_timeout = 60，保持在 FIN_WAIT_2 状态的时间

**TIME_WAIT 状态**

- MSL（Maxinmum Segment Lifetime）：报文最大生存时间
- TIME_WAIT 状态会维持 2MSL 的时长，保证至少一次报文的往返时间内端口是不可复用的。

**TIME_WAIT 优化**

- net.ipv4.tcp_tw_reuse = 1
  - 开启后，作为客户端时新连接可以使用仍然处于 TIME_WAIT 状态的端口
  - 由于 timestamp 的存在，操作系统可以拒绝迟到的报文（net.ipv4.tcp_timestamps = 1）

- net.ipv4.tcp_tw_recycle = 0
  - 开启后，同时作为客户端和服务器都可以使用 TIME_WAIT 状态的端口
  - 不安全，无法避免报文延迟，重复等给新连接造成混乱
- net.ipv4.tcp_max_tw_buckets = 262144 
  - time_wait 连接的最大数量
  - 超出后直接关闭连接

### 使用stub_status模块监控Nginx状态

模块：`ngx_http_stub_status_module` ，通过 --with-http_stub_status_module启用模块

功能：通过 HTTP 接口，实时监测 nginx 的连接状态。统计数据放在共享内存中，所以统计值包含所有 worker 进程，且执行 reload 不会导致数据清零，但热升级会导致数据清零。

语法：`stub_status;`

**stub_status 模块的监控项**

```
Active connections: 2 
server accepts handled requests
 25 25 39 
Reading: 0 Writing: 1 Waiting: 1
```

- Active connections：当前客户端与Nginx间的TCP连接数，等于下面 Reading、Writing、Waiting 数之和
- accepts：自 Nginx 启动起，与客户端建立过的连接总数。
- handled：自 Nginx 启动起，处理过的客户端连接总数。如何超出 worker_connections 配置，该值与 accepts 相同
- requests：自 Nginx 启动起，处理过的客户端请求总数。由于存在 HTTP Keep-Alive请求，故 requests 值会大于 handled 值。
- Reading：正在读取 HTTP 请求头部的连接总数
- Writing：正在向客户端发送响应的连接总数
- Waiting：当前空闲的 HTTP keep-alive 连接总数