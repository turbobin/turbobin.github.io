---
layout:     post
title:      Spring Cloud 及 Eureka 注册中心
subtitle:   
date:       2019-01-07
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
tags:
    - [微服务, spring cloud]
---
### 简述 ###
Spring Cloud是微服务的“全家桶”，包含了很多的子项目，每一个子项目都是一种微服务的解决方案，它利用Spring Boot的开发风格对各种比较成熟的服务框架进行了二次封装，最终留出了一套简单易用的开发工具包。

#### Spring Cloud子项目介绍 ####

![]({{site.url}}/img/java/springcloud-01.png)
#### Spring Cloud版本介绍 ####
Spring Cloud版本并没有像Spring Boot那样采用1.x.x，2.x.x的方式，而是采用Dalston SR5、Edgware SR5、Edgware SR5这样的名称，这是因为，Spring Cloud不像Spring社区其他项目那样相对独立，它是拥有诸多子项目的大型综合项目. 可以说是对微服务架构解决方案的综合套件的组合，其包含的各个子项目也都是进行独立的更新和迭代，各自都维护自己的发布版本号.因此每一个Spring Cloud的版本都会包含多个不同版本的子项目，为了管理每一个版本的子项目清单，避免Spring Cloud的版本号与其子项目的版本号相混淆，没有采用版本号的方式，而是通过命名的方式。

**各项目版本对照：**
<table class="tableblock frame-all grid-all spread">
<caption class="title" align="center">Table 1. Release train Spring Boot compatibility</caption>
<colgroup>
<col style="width: 30%;">
<col style="width: 30%;">
</colgroup>
<thead>
<tr>
<th class="tableblock halign-left valign-top">Release Train</th>
<th class="tableblock halign-left valign-top">Boot Version</th>
</tr>
</thead>
<tbody>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">Greenwich</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.1.x</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">Finchley</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.x</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">Edgware</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.5.x</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">Dalston</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.5.x</p></td>
</tr>
</tbody>
</table>

<table class="tableblock frame-all grid-all spread">
<caption class="title">Table 2. Release train contents</caption>
<colgroup>
<col style="width: 25%;">
<col style="width: 20%;">
<col style="width: 20%;">
<col style="width: 35%;">
</colgroup>
<thead>
<tr>
<th class="tableblock halign-left valign-top">Component</th>
<th class="tableblock halign-left valign-top">Edgware.SR5</th>
<th class="tableblock halign-left valign-top">Finchley.SR2</th>
<th class="tableblock halign-left valign-top">Finchley.BUILD-SNAPSHOT</th>
</tr>
</thead>
<tbody>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-aws</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.2.3.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-bus</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.3.3.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.0.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-cli</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.4.1.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.0.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-commons</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.3.5.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-contract</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.2.6.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-config</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.4.5.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-netflix</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.4.6.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-security</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.2.3.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-cloudfoundry</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.1.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-consul</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.3.5.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-sleuth</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.3.5.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-stream</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">Ditmars.SR4</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">Elmhurst.SR1</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">Elmhurst.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-zookeeper</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.2.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.0.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-boot</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.5.16.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.6.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.7.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-task</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.2.3.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.0.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.1.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-vault</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.1.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-gateway</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-openfeign</p></td>
<td class="tableblock halign-left valign-top"></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">2.0.2.BUILD-SNAPSHOT</p></td>
</tr>
<tr>
<td class="tableblock halign-left valign-top"><p class="tableblock">spring-cloud-function</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.0.1.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.0.0.RELEASE</p></td>
<td class="tableblock halign-left valign-top"><p class="tableblock">1.0.1.BUILD-SNAPSHOT</p></td>
</tr>
</tbody>
</table>

>Finchley builds and works with Spring Boot 2.0.x, and is not expected to work with Spring Boot 1.5.x.  
Note: The Dalston release train will reach end-of-life in December 2018. Edgware will follow the end-of-life cycle of Spring Boot 1.5.x.  
The Dalston and Edgware release trains build on Spring Boot 1.5.x, and are not expected to work with Spring Boot 2.0.x.

从官网介绍可知，基于Spring Boot 2.0.x的Spring Cloud只能用Finchley版本，Spring Boot 1.5.x只能用Spring Cloud Dalston和Edgware版本。
当前最新稳定版本：
![]({{site.url}}/img/java/springcloud-02.png)

### Eureka 注册中心 ###
Spring Cloud提供了多种注册中心的支持，如：Eureka、ZooKeeper等。官方推荐使用Eureka。
Spring Cloud Eureka是Spring Cloud Netflix微服务套件中的一部分，它基于Netflix Eureka做了二次封装。主要负责完成微服务架构中的服务治理功能。
原理图如下：
![]({{site.url}}/img/java/eureka-01.png)

Eureka包含两个组件：Eureka Server和Eureka Client。
* Eureka Server提供服务注册服务，各个节点启动后，会在Eureka Server中进行注册，这样EurekaServer中的服务注册表中将会存储所有可用服务节点的信息，服务节点的信息可以在界面中直观的看到。
* Eureka Client是一个java客户端，用于简化与Eureka Server的交互在应用启动后，将会向Eureka Server发送心跳,默认周期为30秒，如果Eureka Server在多个心跳周期内没有接收到某个节点的心跳，Eureka Server将会从服务注册表中把这个服务节点移除(默认90秒)。

Eureka Server之间通过复制的方式完成数据的同步，Eureka还提供了客户端缓存机制，即使所有的Eureka Server都挂掉，客户端依然可以利用缓存中的信息消费其他服务的API。综上，Eureka通过心跳检查、客户端缓存等机制，确保了系统的高可用性、灵活性和可伸缩性。



**推荐阅读：**

[Spring Cloud 最佳项目构建](https://turbobin.github.io/2019/01/10/best-springcloud-practice/)

>写技术博客不易，转载请注明出处，附上本原文链接, 谢谢合作。