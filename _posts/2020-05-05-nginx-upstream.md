---
layout:     post
title:      Nginx学习笔记-反向代理与负载均衡
subtitle:
date:       2020-05-05
author:     turbobin
header-img:
catalog: true
category: 技术
tags:
    - nginx
---

### 负载均衡策略：round-robin

**指定上游服务的 upstream 和 server 指令**：

语法：

- `upstream name {...};`
- `server address [parameters];`

功能：指定一组上游服务器地址，其中，地址可以是域名、IP地址或者 unix socket 地址。可以在域名或者 IP 地址后加端口，如果不加，则默认 80 端口。

通用参数：

- backup：指定当前 server 为备份服务，仅当主 server 不可用时，请求才会转发到该 server 上
- down：标识某台服务已经下线，相当于注释此 server 

**加权 Round-Robin 负载均衡算法**：

功能：以加权轮询的方式访问 server 指令指定的上游服务。集成在 Nginx 的 upstream 框架中

指令：

- weight：服务访问的权重，默认是 1
- max_conns：server 的最大并发连接数，仅作用于单 worker 进程。默认是 0，表示没有限制。
- max_fails：在 file_timeout 时间段内，最大的失败次数。当达到最大失败时，会在 fail_timeout 秒内这台 server 不允许再次被选择。
- fail_timeout：单位为秒，默认为 60。表示指定一段时间内，最大的失败次数 max_fails；到达最大的失败次数后，该 server 不能访问的时间。

**对上游服务使用 keepalive 长连接**：

功能：通过复用连接，降低 nginx 与上游服务器建立、关闭连接的消耗，提升吞吐量同时降低时延。

模块：`ngx_http_upstream_keepalive_module`，默认编译进 nginx，可通过 --without-http_upstream_keeplive_module 移除

> 由于 keepalive 只在 http 1.1 生效，因此要对上游连接的 http 头部限定：
>
> proxy_http_version 1.1;
>
> proxy_http_header Connection "";

**upstream_keepalive 的指令**：

- `keepalive connections;`
- 1.15.3 版本后新增指令`keepalive_requests number;`默认 限制100 个长连接请求
- 1.15.3 版本后新增指令`keepalive_timeout timeout;`默认限制 60s 的长连接超时时间

**指定上游服务域名的 resolver 指令：**

- `resolver address ... [valid=time][ipv6=on | off];`，表示指定一个解析上游服务的 DNS 解析地址。
- `resolver_timeout time;`访问超时时间，默认 30s

### 负载均衡哈希算法：IP hash 与 hash 模块

**基于客户端 ip 地址的 Hash  算法实现负载均衡**

模块：`ngx_http_upstream_ip_hash_module`，默认编译进 nginx 中，可通过 `without-http_upstream_ip_hash_module`禁用。

语法：`ip_hash;` 用在 `upstream`模块下。

功能：以客户端 iP 地址（remote_addr）作为 hash 算法的关键字，映射到特定的上游服务器中。

- 对 IPv4 地址使用前3个字节作为关键字，对 IPV6 则使用完整地址
- 可以基于 realip 模块修改用于执行执行算法的 ip 地址

**基于任意关键字实现 Hash 算法的负载均衡**

模块：`ngx_http_upstream_hash_module`，默认编译进nginx，可通过`without-http_upstream_hash_module`禁用。

语法：`hash key [consistent];` 用在 `upstream`模块下。

功能：通过指定关键字作为 hash key，基于 hash 算法映射到特定的上游服务器中。

- 关键字可以含有变量，字符串。

### 一致性哈希算法：hash 模块

语法：`hash key consistent;`

hash 算法引发的问题：当宕机或者扩容时，hash 算法引发大量路由变更，可能导致缓存大范围失效。

一致性hash 算法：将服务器均匀的分配在一个 0 ~ 2^32  的 hash 环上，hash 后的值沿顺时针分配在离的最近的服务器节点上。当宕机或扩容时，在任意两个服务器之间添加一个节点，那么只会影响两个服务器之间的哈希节点值，而对其他服务器节点没有影响。

![image-20200502232808681](https://github.com/turbobin-cao/images/raw/main/image-20200502232808681.png)

![image-20200502232831008](https://github.com/turbobin-cao/images/raw/main/image-20200502232831008.png)

### 优先选择最少连接的上游服务器

模块：`ngx_http_upstream_least_conn_module`，通过`--without-http_upstream_least_conn_module`禁用模块。

语法：`least_conn;`用于 `upstream`模块下。

功能：从所有上游服务器中，找出当前并发数连接最少的的一个，将请求转发到它（如果出现多个最少连接服务器的并发连接数都是一样的，使用 round-robin算法）。

### 使用共享内存使负载均衡策略对所有 worker 进程生效

模块：`ngx_http_upstream_zone_module`，默认编译进 nginx 中

语法：`zone name [size];`

功能：分配出共享内存，将其他 upstream 模块定义的负载均衡策略数据，运行时每个上游服务的状态数据放在共享内存上，以对所有 nginx worker 进程生效

### upstream 模块提供的变量(不含cache)

|           变量           |                             说明                             |
| :----------------------: | :----------------------------------------------------------: |
|      upstream_addr       | 上游服务器的 ip 地址，格式为可读的字符串，如：127.0.0.1:8012 |
|  upstream_connect_time   |      与上游服务建立连接消耗的时间，单位为秒，精确到毫秒      |
|   upstream_header_time   | 接受上游服务器发回响应中 http 头部所消耗的时间，单位为秒，精确到毫秒 |
|  upstream_response_time  |         接受完整的上游服务响应所消耗的时间，单位为秒         |
|    upstream_http_名称    |                 从上游服务返回的响应头部的值                 |
| upstream_bytes_received  |                 从上游服务接收到的响应字节数                 |
| upstream_response_length |          从上游服务返回的响应包体的长度，单位为字节          |
|     upstream_status      |    上游服务返回的HTTP状态码，如果未连接上，该变量值为502     |
|   upstram_cookie_名称    |       从上游服务发回的响应头Set-Cookie中取出的cookie值       |
|  upstream_trailer_名称   |                 从上游服务的响应尾部取到的值                 |

### HTTP 反向代理流程

![image-20200503185243834](https://github.com/turbobin-cao/images/raw/main/image-20200503185243834.png)

### proxy模块：proxy_pass 指令

![image-20200503121156426](https://github.com/turbobin-cao/images/raw/main/image-20200503121156426.png)

**示例：**

代理：

```nginx
upstream proxyups {
    server 127.0.0.1:8012 weight=1;
}

server {
    server_name proxy.turbobin.com;
    
    location /a {
        proxy_pass http://proxyups;
    }
}
```

上游：

```nginx
server {
    listen 8012;
    default_type text/plain;
    return 200 '8012 server response. uri: $uri \n';
}
```

当请求代理服务器时：`curl http://proxy.turbobin.com/a/b/c`时，返回`8012 server response. uri: /a/b/c`

修改代理服务器 proxy_pass：`proxy_pass http://proxyups/www;`，再次请求，将返回：``8012 server response. uri: /www/b/c`， `/a`替换成了 `/www`。

### proxy 模块：根据指令修改发往上游的请求

**生成发往上游的请求行**

- `proxy_method POST|GET;`修改请求方式
- `proxy_http_version 1.0|1.1;`修改http协议版本，默认为 http1.0

**生成发往上游的请求头部**

- `proxy_set_header field value;`

    默认为 `proxy_set_header Host $proxy_host;` 

    	  		  `proxy_set_header Connection close;`

    注意：若value值为空字符串，则整个 header 都不会向上游发送

- `proxy_pass_requet_headers on | off;`是否发送头部的开关，默认为 on

**生成发往上游的包体**

- `proxy_pass_request_body on | off;` 默认为 on
- `proxy_pass_set_body value;` 设置包体

### 接受用户请求包体的方式

两种方式：收完包体再转发 或者边收边转发

配置：`proxy_requst_buffering on | off;`

- 收完包体再转发：on ， 默认值，适用三种场景：客户端网速慢，上游服务并发处理能力低，适用高吞吐量。
- 边收边转发：off，意味着更及时的响应，可以降低 nginx 读写磁盘的消耗，一旦开始发送内容，`proxy_next_upstream` 指令功能失效。

接受包体内存分配指令：

- `client_body_buffer_size size;` 默认 size 为 8k 或 16 k。
- `client_body_in_single_buffer on | off;`表示是否将请求的包体全部放在内存中，默认为 off。

存在包体时，接受包体所分配的内存

- 若接受头部时，已经接收完全部的包体，则不分配。
- 若剩余待接收的包体长度小于 `client_body_buffer_size`，则仅分配所需大小
- 分配`client_body_buffer_size`大小的内存接收包体。
  - 当关闭包体缓存时，该内存上的内容及时发送给上游。
  - 当打开包体缓存，该段内存大小用完时，写入临时文件，释放缓存。

最大包体长度限制：

`client_max_body_size size;` 默认为 1 M。

仅对请求头部中含有 Content-Length 有效超出最大长度后，返回 413 错误。

临时文件路径格式：

- `client_body_temp_path path [level1[level2[level3]]];`默认目录为 `client_body_temp`（在 nginx 下自动创建），后面可以跟多级子目录
- `client_body_in_file_only on | clean | off;`默认 off，表示包体必须存放在文件中。 on 表示用户上传的 body 会一直存放在文件中，clean 表示请求处理完成则会把文件清除掉。off 也会把文件清除，但是对于比较小的 body 则不会存放在文件中。

读取包体的超时设置：

- `client_body_timeout time;`默认 60 s （读取包体超时时，会返回 408 错误）

### 与上游服务建立连接

- 设置连接超时：`proxy_connect_timeout time;`默认 60 s。超时后会向客户端生成http响应，响应码为 502。

- 当建立连接返回错误码时，可以指定另一台服务器作为上游服务：`proxy_next_upstream http_502 |...;` 默认`proxy_next_upstream error timeout;`
- 上游启用 TCP keepalive：`proxy_socket_keepalive on | off;` 默认 off
- 上游启动 HTTP 的 keepalive：在 upstream 模块中加上`keepalive connections;`指定用于长连接的连接数。`keeplive_request number;`用于指定长连接的请求数，默认为 100。

- 修改 TCP 连接中的 local address：`proxy_bind address [transparant] | off;` *address* 可以使用 `$remote_addr` ，如果地址不是所在机器的 IP 地址，则需要加上 transparent
- 当客户端关闭连接时，判断是否忽略连接：`proxy_ignore_client_abort on | off;`默认为 off

### 接受上游的响应

- 定义接收上游响应的缓存大小：`proxy_buffe_size size;` 默认 4k 或 8k。也限定了上游响应 header 的最大值，当超出时，error.log 中会打印一条：upstream sent too big header.
- 接收响应包体的方式：`proxy_buffering on | off;` 默认为 on。表示接受完完整包体之后再转发。off 时 表示边接受边转发。
- 包体写入临时文件相关指令：
  - `proxy_max_temp_file_size size;`默认 1024 M
  - `proxy_temp_file_write_size size;` 默认 8k 或 16k
  - `proxy_temp_path path [level1 [level2 [level3]]];`
- 及时转发包体：`proxy_busy_buffers_size size;`默认 8k 或 16k
- 接收上游超时设置：`proxy_read_timeout time;` 默认 60s
- 限速：`proxy_limit_rate rate;`默认 rate 为0，表示不限速。
- 上游包体的持久化：
  - 设置权限：`proxy_store_access users:rw;`设置读写权限
  - 开关：`proxy_store on | off | string;`

### 反向代理缓存流程

**发起请求部分**

![image-20200503221759805](https://github.com/turbobin-cao/images/raw/main/image-20200503221759805.png)

**接收上游响应**

![image-20200503221849269](https://github.com/turbobin-cao/images/raw/main/image-20200503221849269.png)

### 清除缓存模块

清除缓存可以用第三方模块：`ngx_cache_purge`: https://github.com/FRiCKLE/ngx_cache_purge

使用 `--add-module=` 指令添加模块到 nginx 中

功能：接收到指定请求后立刻清除缓存

指令：

- `proxy_cache_purse on | off |<method>[from all|<ip>[...<ip>]];`可以对某一方法或某几个ip清除缓存。可以配置在 http、server、location 模块下。
- `proxy_cache_purse zone_name key;`只能配置在 location 模块下。

### uwsgi、fastcgi、scgi 七层反向代理的对照表

**相关文档：**

http://nginx.org/en/docs/http/ngx_http_proxy_module.html

http://nginx.org/en/docs/http/ngx_http_uwsgi_module.html

http://nginx.org/en/docs/http/ngx_http_fastcgi_module.html

http://nginx.org/en/docs/http/ngx_http_scgi_module.html

**构造请求内容**

![image-20200503222936211](https://github.com/turbobin-cao/images/raw/main/image-20200503222936211.png)

**建立连接并发送请求**

![image-20200503223022166](https://github.com/turbobin-cao/images/raw/main/image-20200503223022166.png)

**接收上游响应**

![image-20200503223109325](https://github.com/turbobin-cao/images/raw/main/image-20200503223109325.png)

**转发响应**

![image-20200503223143942](https://github.com/turbobin-cao/images/raw/main/image-20200503223143942.png)

**SSL相关**

![image-20200503223215936](https://github.com/turbobin-cao/images/raw/main/image-20200503223215936.png)

**缓存类指令**

![image-20200503223250780](https://github.com/turbobin-cao/images/raw/main/image-20200503223250780.png)

![image-20200503223307188](https://github.com/turbobin-cao/images/raw/main/image-20200503223307188.png)

**独有配置**

![image-20200503223342827](https://github.com/turbobin-cao/images/raw/main/image-20200503223342827.png)

### memcached 反向代理

模块：`ngx_http_memcached_module`默认编译进 nginx ，可通过 --without-http_memcached_module禁用功能。

功能：

- 将 HTTP 请求转换为 memcached 协议中的 get 请求，转发请求至上游 memcached 服务

- get 命令：`get <key> * \r\n`

- 控制命令：`<command name><key><flags><expire time><bytes>[noreply]\r\n`， 如：

  连接 memcached `telnet 127.0.0.1 112211`

  ```
  set hello 0 0 5		# 设置key为hello，flag为0，不过期，value长度为5个字节
  world				# value 值为 world
  ```

- 通过设置 memcached_key 变量构造key键

**memcached 指令**

![image-20200503235708467](https://github.com/turbobin-cao/images/raw/main/image-20200503235708467.png)

**示例：**

```nginx
server {
    server_name memcached.turbobin.com;
    default_type text/plain;
    
    location /get {
        set $memcached_key "$arg_key";	# 从参数中获取key值
        memcached_gzip_flag 2;
        memcached_pass localhost:11211;
    }
}
```

访问：`curl memcached.turbobin.com/get?key=hello` 将返回 memcached 的 hello 值：world

`memcached_gzip_flag`表示如果 key 对应的 value 值是经过 gzip 压缩的，设置此变量后，返回给浏览器的 header 中将会添加 `Content-Encoding: gzip`，不如不设置，那么返回给浏览器的数据将无法解析。

### websocket 反向代理

模块：`ngx_http_proxy_module`

配置：

```nginx
# 加入以下 3 个指令即可
location / {
    proxy_http_version 1.1;
	proxy_set_header Upgrade $http_upgrade;
	proxy_set_header Connection "upgrade";
}
```

**HTTP 协议升级为 websocket**

![image-20200504110311249](https://github.com/turbobin-cao/images/raw/main/image-20200504110311249.png)

**websocket 测试工具：**

http://www.websocket.org/echo.html

![image-20200504110854381](https://github.com/turbobin-cao/images/raw/main/image-20200504110854381.png)

配置nginx

```nginx
server {
    listen 80;
    server_name websocket.turbobin.com;
    access_log logs/ws.log;
    
    location / {
        proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "upgrade";
        proxy_pass http://echo.websocket.org;
    }
}
```

抓包验证：`tcpdump -i eth0 port 80 and host echo.websocket.org -A`

### 使用分片提升缓存效率

模块：`ngx_slice_module`，默认未编译进 nginx ，可通过 --with-http_slice_module 启动功能

功能：通过 range 协议将大文件分解成多个小文件，更好的有用缓存为客户端的 range 协议服务。

**slice 模块的运行流程**

![image-20200504113411000](https://github.com/turbobin-cao/images/raw/main/image-20200504113411000.png)

**示例：**

```nginx
server {
    server_name slice.turbobin.com;
    error_log logs/cacherr.log debug;
    
    location / {
        proxy_cache three;
        
        #slice	1m;		# 按 1M 单位发送
        #proxy_cache_key	$uri$is_args$args$slice_range;
        #proxy_set_header Range $slice_range;
        
        proxy_cache_valid 200 206 1m;
        add_header X-Cache-Status $upstream_cache_status;
        
        proxy_pass http://localhost:8012;
    }
}
```

先注释 slice 配置，当使用 range 协议访问一个大文件的某一段字节时，如：

```
curl -r 5000010-5000019 slice.turbobin.com/video.mp4 -I
```

返回 header 中 Content-Length 为 10 字节，而上游服务器返回的是 `video.mp4` 文件完整的大小。如果并发访问这个文件将会出现很大的问题。

如果配置了 slice，则上游将按指定的单位大小返回（如上面配置了 1M 大小）。

应用：此模块应用于客户端使用 range 协议实现断点续传，多线程下载时的场景。

### 缓存文件信息：open_file_cache

```nginx
server {
    listen 80;
    root html;
    location / {
        open_file_cache max=10 inactive=60s; # 在某个worker进程的内存中最多缓存多少个文件，超过使用LRU缓存淘汰，可以设置文件多久未访问时就移除它。
        open_file_cache_min_uses 1;	# 至少访问多少次才进行缓存
        open_file_cache_valid 60s;	# 经过多少时间后去确认缓存中的文件是否有效，如果文件有更新，将会更新缓存。
        open_file_cache_errors on;	# 对访问错误的信息是否进行缓存
    }
}
```

Tips：使用`strace -p PID` 可以追踪进程的请求信息。关注文件打开和关闭句柄（open、close）、 sendfile 信息

### 搭建 HTTP 2.0 服务

模块：`ngx_http_v2_module`，默认未编译进 nginx，可通过 --with-http_v2_module 编译进 nginx 来支持 http2 协议

功能：对客户端提供 http2 协议提供基本功能

前提：必须开启 TLS/SSL 协议

使用方法：添加`listen 443 ssl http2;`

**nginx 推送资源**

- `http2_push_preload on | off;` 默认为 off
- `http2_push uri | off;`默认为 off，可以有 nginx 层直接向客户端推送指定资源。

**测试 nginx http2 协议的客户端工具**

安装：

- 在 https://github.com/nghttp2/nghttp2/releases 下载安装
- centos 使用 `yum install nghttp2`安装

测试：

```nginx
server {
    listen 4430 ssl http2;
    server_name http2.turbobin.com;
    
    ssl_certificate  /usr/local/nginx/conf/vhost/2020_1_turbobin.com_bundle.crt;
    ssl_certificate_key  /usr/local/nginx/conf/vhost/2020_2_turbobin.com.key;
    
    root html;
    location / {
        http2_push /mirror.txt;
        http2_push /video.mp4;
        
    }
    
    location test_http2/ {
        add_header Link "</style.css>; as=style; rel=preload";	# 推送 style.css
        http2_push_preload on;	# 主动推送开启
    }
}
```

使用 http2 工具来访问：`nghttp -ns https://http2.turbobin.com:4430/`

将会看到推送了 mirror.txt 和 video.mp4

当访问：`ngttp -ns https://http2.turbobin.com:4430/test_http2/index.html`

将会看到推送了 index.html 和 style.css 

**其他配置：**

- 最大并行推送数：`http2_max_concurrent_pushes numbers;` 默认 numbers 为 10；
- 超时控制：
  - `http2_recv_timeout time;`接收超时，默认 30s；
  - `http2_idle_timeout time;` 空闲多久关闭连接，默认 3m（3分钟）；
- 最大并行 stream 数：`http2_max_concurrent_streams numbers`默认为 128；
- 最大压缩后 http header 的大小：`http2_max_filed_size size;`默认 4k；
- 连接最大处理请求数：`http2_max_requests numbers;` 默认为 1000；
- 设置响应包体分片的大小：`http2_chunk_size size`，默认为 8k；
- 缓存区大小设置：
  - `http2_recv_buffer_size size;`默认256k；
  - 对http头部做完解压以后最大的 header 大小：`http2_max_header_size size;`默认16k；
  - 针对每个请求预读的大小：`http2_body_preread_size size;`默认64k；

### gRPC 反向代理

模块：`ngx_http_grpc_module`，默认编译进 nginx 中，依赖于 http2 协议，所以需要先编译 `ngx_http_v2_module`模块

**grpc 指令对照表**

![image-20200504142109909](https://github.com/turbobin-cao/images/raw/main/image-20200504142109909.png)

![image-20200504142152061](https://github.com/turbobin-cao/images/raw/main/image-20200504142152061.png)

**示例：**

```nginx
upstream grpcservers {
  server localhost:50011;
  server localhost:50012;
  server localhost:50013;
}

server {
    listen 50051 http2;
    access_log /data2/wwwlogs/access.log access;
    location / {
        grpc_pass grpc://grpcservers;
    }
}
```

### stream 模块

**功能：**代理 TCP 、UDP 服务。启用 stream 模块需要在编译时加上 `--with-stream`

**请求处理的 7 个阶段：**

![image-20200504145725010](https://github.com/turbobin-cao/images/raw/main/image-20200504145725010.png)

**传输层相关变量：**

![image-20200504145837118](https://github.com/turbobin-cao/images/raw/main/image-20200504145837118.png)

![image-20200504145859969](https://github.com/turbobin-cao/images/raw/main/image-20200504145859969.png)

![image-20200504145939411](https://github.com/turbobin-cao/images/raw/main/image-20200504145939411.png)

**Nginx 系统变量：**

![image-20200504150021827](https://github.com/turbobin-cao/images/raw/main/image-20200504150021827.png)

**示例：**

```nginx
stream {
    error_log logs/stream.log debug;
    server {
        listen 10002 proxy_protocol;
        return '10002 server get ip: $remote_addr \n'; 
    }
    
    server {
        listen 10003 proxy_protocol;
        return '10003 server get ip: $remote_addr \n'; 
    }
    
    server {
        listen 10004;
        # listen 10004 proxy_protocol;
        return '10004 vars: 
            bytes_received: $bytes_received
            bytes_sent: $bytes_sent
            proxy_protocol_addr: $proxy_protocol_addr
            proxy_protocol_port: $proxy_protocol_port
            remote_addr: $remote_addr
            remote_port: $remote_port
            server_addr: $server_addr
            server_port: $server_port
            session_time: $session_time
            status: $status
            protocol: $protocol
            ';
    }
}
```

测试变量：`telnet localhost 10004`，将返回：

```
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
10004 vars: 
            bytes_received: 0
            bytes_sent: 0
            proxy_protocol_addr: 
            proxy_protocol_port: 
            remote_addr: 127.0.0.1
            remote_port: 46094
            server_addr: 127.0.0.1
            server_port: 10004
            session_time: 0.000
            status: 000
            protocol: TCP
            Connection closed by foreign host.
```

### proxy_protocol 协议

stream 模块建立的 TCP 连接是端到端的，如果中间加了 CDN 代理，则无法获取到客户端真实的 ip 地址（http 可以从 header 中获取），这时候可以使用 proxy_protocol 协议。

**proxy_protocol 协议：**

![image-20200504185653936](https://github.com/turbobin-cao/images/raw/main/image-20200504185653936.png)

超时控制：`proxy_protocol_timeout time;` 默认 30 s

**stream 处理 proxy_protocol 流程：**

![image-20200504185905902](https://github.com/turbobin-cao/images/raw/main/image-20200504185905902.png)

### post_accept  阶段： realip 模块

功能：通过 proxy_protocol 协议取出客户端真实 ip 地址，并写入 remote_addr 及 remote_port 变量中，同时使用 realip_remote_addr 和 realip_remote_port 保留TCP 连接中获得的原始地址。

模块：`ngx_stream_realip_module` 需要通过 --with-stream_realip_module 启动功能。

语法：`set_real_ip_from address | CIDR | unix;`

### stream 反向代理

**反向代理指令对照表**

![image-20200504214024999](https://github.com/turbobin-cao/images/raw/main/image-20200504214024999.png)

**stream ssl 指令对照表**

![image-20200504214119706](https://github.com/turbobin-cao/images/raw/main/image-20200504214119706.png)

### UDP 反向代理

UDP 虽然不是面向连接的协议，但是有面向 session 的属性，发送消息里有 source ip 和 source port，也是上游服务 UDP 报文的 dest ip 和 dest port，而 UDP 协议也是可以原路返回的。

**配置指令：**

`proxy_requests number;`（1.15.7 版本） 默认为 0：指定从一次会话 session 中最多从客户端收到多少报文就结束 session 

- 仅会话结束时才会记录 access 日志
- 同一个会话中，nginx 使用同一个端口连接上游服务
- 设置为 0 表示不限制，每次请求都会记录 access 日志

`proxy_response number;`：指定对应一个请求报文，上游返回多少个响应报文（与 proxy_timeout 结合使用，控制上游服务是否不可用）。