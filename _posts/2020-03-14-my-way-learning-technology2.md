---
layout:     post
title:      我的技术学习之路（二）
subtitle:   我的坑
date:       2020-03-14
author:     turbobin
header-img: 
catalog: true
category: 其他
tags:
    - 
---

距离上一篇写 [我的技术学习之路](https://turbobin.site/2018/12/12/my-way-learning-technology.html) 已经过去了一年多了，去年 4 月份我成功转型来到了一家做运动的互联网公司，技术栈又回归了 Python 后端开发。这一年做了数不清的需求，技术能力也有了很大提升，但由于平时太忙（当然这是借口），博客停更了很长时间了，一直都没有时间好好总结一下。

## 从 Java 到 Python

做 Java 项目期间接触到了 Spring 全家桶、Dubbo、Zookeeper 等技术，这些都是很不错的技术栈，但是由于我入坑时间晚，平常学到的也只是在框架层面，想要突破框架深入技术底层，感觉至少还需要 3 ~ 5 年时间，这是我耗不起的。而由于用 Java 开发项目实在效率太低了，Debug、修改、编译、重启服务验证，半天时间就过去了。为了我的头发，我决定重新寻找 Python 开发的工作。最后很幸运，成功入职了一家互联网公司，职位是 Python 后台开发工程师。

## 从 IDE 到 VIM

之前写代码，用的是 Pycharm、IDEA，有代码智能提示、自动格式化、强大的 Debug 工具等等。现在公司强制要求使用 VIM，开发环境一切都在 Linux。一开始一切都很不习惯，并且深刻体会到了自己的弱鸡，原来离开了 IDE 我就没办法写代码了。虽然之前也熟悉 VIM 基本操作，折腾过 Linux，但是使用 VIM 开发项目还从来没有遇到过。经过了一个多礼拜稍微陡峭的学习曲线后，我慢慢适应了 VIM 的一些骚操作，并且感觉写代码能力大增。

我觉得每个程序员都应该适应使用 VIM 编写代码，现在各种强大 IDE 工具已经阉割了程序员的代码能力。脱离工具，脱离代码智能提示，剩下的才是你真正的编程能力。

这里推荐耗子叔的 [简明VIM练级攻略](https://coolshell.cn/articles/5426.html)。

## 从 Python 到后端技术架构

后端基本的服务都是使用的腾讯云，目前共有云服务器实例 63 台，MySQL数据库 29 台，Redis 包括标准版和集群版实例共 11 台，Memcached 实例 11 台，此外还有云域名解析，云短信服务，七牛云存储服务等等。

后端架构基本如下：

![后端架构图](https://github.com/turbobin-cao/images/raw/main/后端架构图.png)

C 端用通过 App 发送请求，经过域名解析到离地域最近的机器，经过Nginx转发，通过内网转发到对应的业务机器集群，集群选择一台机器处理请求，通过 uwsgi 连接 Python 框架，Python 操作数据库、缓存或队列后返回对应的数据给请求端。