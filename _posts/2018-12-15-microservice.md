---
layout:     post
title:      微服务架构
subtitle:   
date:       2018-12-15
author:     turbobin
header-img: img/post-bg-rwd.jpg
catalog: true
tags:
    - 微服务
---

> 本篇文章引用了一些网上图片和已出版书籍。意在更详细说明微服务概念，如有不妥，请联系我删除。

### 前言
近几年，微服务架构在后端技术社区非常火，被认为是IT未来架构的方向，很多业务体量大、业务场景多，对分布式，高并发有一定要求的互联网公司很早就在使用微服务架构。
现在，微服务已经不仅仅只应用在一线互联网公司，由于微服务架构的诸多优点，以及微服务技术框架的成熟，许多微服务开发中遇到的问题都有了一整套的解决方案，如 Spring Cloud，Dubbo 等，因此，微服务在后端的架构和开发中已经越来越普及。

随着互联网的快速发展，网站应用的规模不断扩大，为应对流量的激增带来的网络压力，后端应用架构的技术也在逐渐发生变革，到目前为止，其发展历程基本经历了从单体架构、垂直应用架构、分布式架构、SOA架构、再到微服务架构。
![]({{site.url}}/img/java/microservice-01.jpg)
![]({{site.url}}/img/java/microservice-02.jpg)

### 单体架构
当网站流量很小时，只需一个应用，将所有功能都部署在一起，以减少部署节点和成本。此时，用于简化增删改查工作量的数据访问框架(ORM)是关键。
![]({{site.url}}/img/java/microservice-03.jpg)

### 垂直应用架构
当访问量逐渐增大，单一应用增加机器带来的加速度越来越小，将应用拆成互不相干的几个应用，以提升效率。此时，用于加速前端页面开发的Web框架(MVC)是关键。

### 分布式架构
当垂直应用越来越多，应用之间交互不可避免，将核心业务抽取出来，作为独立的服务，逐渐形成稳定的服务中心，使前端应用能更快速的响应多变的市场需求。此时，用于提高业务复用及整合的分布式服务框架(RPC)是关键。

### 面向服务的SOA架构
当服务越来越多，容量的评估，小服务资源的浪费等问题逐渐显现，此时需增加一个调度中心基于访问压力实时管理集群容量，提高集群利用率。此时，用于提高机器利用率的资源调度和治理中心(SOA)是关键。
![]({{site.url}}/img/java/microservice-04.jpg)
![]({{site.url}}/img/java/microservice-05.jpg)

### 微服务架构
微服务架构在某种程度上是SOA架构发展的下一步。就目前来说，微服务并没有一种很严格的定义，每个人的理解都是不一样的。微服务的概念最早来源于Martin Fowler的一篇文章《MicroServices》，文中是这样表述的：
>In short, the microservice architectural style [1] is an approach to developing a single application as a suite of small services, each running in its own process and communicating with lightweight mechanisms, often an HTTP resource API. These services are built around business capabilities and independently deployable by fully automated deployment machinery. There is a bare minimum of centralized management of these services, which may be written in different programming languages and use different data storage technologies.

文章地址：[https://martinfowler.com/articles/microservices.html](https://martinfowler.com/articles/microservices.html)

>译：简单来说，微服务架构风格是一种将一个单一应用程序开发为一组小型服务的方法,每一个服务运行在自己的进程中,服务间通信采用的轻量级通信机制(通常用HTTP资源API). 这些服务围绕业务能力构建并且可通过全自动部署机制独立部署. 这些服务公用一个最小型的集中式的管理,服务可用不同的语言开发,使用不同的数据存储技术.

架构图：
![]({{site.url}}/img/java/microservice-06.jpg)

**微服务架构优点：**
* 易于开发和维护: 一个微服务只会关注一个特定的业务功能，所以它业务清晰、代码量少。开发和维护单个微服务相当简单。而整个应用是若干个微服务构建而成的，所以整个应用也被维持在一个可控状态。
* 单个微服务启动较快: 单个微服务代码量较少，所以启动会比较快。
* 局部修改容易部署: 单个应用只要有修改，就得重新部署整个应用，微服务解决了这样的问题。一般来说，对某个微服务进行修改，只需要重新部署这个服务即可。
* 技术栈不受限: 在微服务架构中，可以结合项目业务及团队的特点，合理选择技术栈。例如某些服务可以使用关系型数据库Mysql,有些服务可以使用非关系型数据库如redis；甚至可根据需求，部分微服务使用Java开发，部分微服务使用Node.js开发。
* 按需收缩: 可根据需求，实现细粒度的扩展。例如，系统中的某个微服务遇到了瓶颈，可以结合这个微服务的业务特点，增加内存、升级CPU或者增加节点。

**微服务架构的缺点：**
* 运维要求较高: 更多的服务意味着更多的运维投入。在单体架构中，只需要保证一个应用的正常运行。而在微服务中，需要保证几十甚至几百个服务正常运行与协作，这给运维带来了很大的挑战。
* 分布式固有的复杂性: 使用微服务构建的是分布式系统。对于一个分布式系统，系统容错、网络延迟等都会带来巨大的挑战。
* 接口调整成本高: 微服务之间通过接口进行通信。如果修改某一个微服务API，可能所有使用该接口的微服务都需要调整。

### 微服务架构技术选型
![]({{site.url}}/img/java/microservice-07.jpg)
![]({{site.url}}/img/java/microservice-08.jpg)

### 微服务解决方案
1. **基于Spring Cloud的微服务解决方案**  
Spring Cloud并不是一个项目,而是一组项目的集合. 在Spring Cloud中包含了很多的子项目.每一个子项目都是一种微服务开发过程中遇到的问题的一种解决方案. 它利用Spring Boot的开发便利性巧妙地简化了分布式系统基础设施的开发，如服务发现注册、配置中心、消息总线、负载均衡、断路器、数据监控等，都可以用Spring Boot的开发风格做到一键启动和部署。Spring Cloud并没有重复制造轮子，它只是将目前各家公司开发的比较成熟、经得起实际考验的服务框架组合起来，通过Spring Boot风格进行再封装屏蔽掉了复杂的配置和实现原理，最终给开发者留出了一套简单易懂、易部署和易维护的分布式系统开发工具包，被称为Spring Cloud“全家桶”。
基于Spring Cloud的微服务落地解决方案可以分为三种：
![]({{site.url}}/img/java/microservice-09.jpg)

2. **基于Dubbo实现微服务解决方案**  
Dubbo是阿里在GitHub上开源的分布式服务治理框架，有一段时间停止了更新维护，期间，当当网基于Dubbo框架升级推出了Dubbox框架。2012年，阿里巴巴重新维护Dubbo，并做了一系列升级更新，因此，我们现在用的最多的还是阿里的Dubbo框架。Duboo最初的未来定位并不是要成为一个微服务的全面解决方案，而是专注于RPC领域，成为微服务生态体系中的一个重要组件。至于微服务化衍生出的服务治理需求，Dubbo正在积极适配开源解决方案，并且已经启动开源项目支持，比如最新开源的Nacos。Nacos的定位是一个更易于帮助构建云原生应用的动态服务发现、配置和服务管理平台。因此，基于Dubbo的微服务解决方案是：Dubbo+Nacos+其他。