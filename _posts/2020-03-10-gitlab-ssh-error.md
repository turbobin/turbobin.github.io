---
layout:     post
title:      Gitlab无法使用ssh问题
subtitle:   
date:       2020-03-10
author:     turbobin
header-img: 
catalog: true
category: 其他
tags:
    - 
---

### 问题描述

gitlab 用 git clone 无法使用 ssh 协议，只能使用 http 协议 clone 代码，为此每次使用 git 远程交互时都要使用密码。

### 问题排查

如：远程 gitlab 仓库为 `git@code.17yund.me:user/Project.git`

需要在本地 api11 机器 git clone 远程 gitlab 机器的代码。

首先在 api11 通过 ssh debug 测试一下：`ssh -Tv git@code.17yund.me`

```
OpenSSH_5.3p1, OpenSSL 1.0.1e-fips 11 Feb 2013
debug1: Reading configuration data /etc/ssh/ssh_config
debug1: Applying options for *
debug1: Connecting to code.17yund.me [139.199.202.113] port 22.
等待一段时间后，连接超时
```

排查：

- 查看是否可以连上 gitlab 机器的 22 端口。

  在确认 gitlab 机器打开端口的情况下，仍然无法通过 ssh 连接，原因有以下：

  1、无法通过 `code.17yund.me` 解析到 gitlab 机器 ip 地址，需要在 api11 添加 gitlab 的内网地址：`vim /etc/hosts`

  ```shell
  127.0.0.1  localhost  localhost.localdomain  VM_80_64_centos
  10.104.185.131  code.17yund.me	# 添加这行
  ```

  2、远程主机拒绝了api11 的 ssh 连接。需要在 gitlab 机器添加 ip 白名单

  `vim /etc/hosts.allow`

  ```
  #
  # hosts.allow   This file contains access rules which are used to
  #               allow or deny connections to network services that
  #               either use the tcp_wrappers library or that have been
  #               started through a tcp_wrappers-enabled xinetd.
  #
  #               See 'man 5 hosts_options' and 'man 5 hosts_access'
  #               for information on rule syntax.
  #               See 'man tcpd' for information on tcp_wrappers
  sshd:10.104.80.64:allow
  sshd:all:deny
  ```

- 查看是否生成 ssh key（在 /root/.ssh 目录下查看）

  若没有生成 ssh key，需要先生成：`ssh-keygen -t rsa -C "root@api11"`

  ```shell
  Generating public/private rsa key pair.
  Enter file in which to save the key (/root/.ssh/id_rsa):		# 这里可以指定其他文件名称，但是一般默认就可以了。之后一路回车
  Enter passphrase (empty for no passphrase): 
  Enter same passphrase again: 
  Your identification has been saved in /root/.ssh/id_rsa.
  Your public key has been saved in /root/.ssh/id_rsa.pub.
  The key fingerprint is:
  71:f6:00:40:5c:f1:b4:27:9c:7c:a1:f8:e7:3a:a2:8e root@api11
  ```

  之后在`/root/.ssh`下会看到生成了两个密钥文件，id_rsa 和 id_rsa.pub。接下来把公钥添加导 gitlab 的 ssh key 中（注意是打开 gitlab 网页个人设置的 SSH Keys 中）

  `cat /root/.ssh/id_rsa.pub `

- 最后再通过 `ssh -Tv git@code.17yund.me` 测试一下，看到最后 `debug1: Exit status 0` 就表示大功告成了。现在可以愉快的通过 ssh 克隆代码了