---
layout:     post
title:      负载均衡：Ribbon
subtitle:   
date:       2019-01-14
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
tags:

   - [微服务, spring cloud]


---

#### 简介

可先参看上一节：[Spring Cloud 最佳项目构建](https://turbobin.github.io/2019/01/10/best-springcloud-practice/)

如果同一个提供者在 Eureka 注册了多个服务，那么消费者如果选择服务呢？

这时，需要在消费端实现服务的负载均衡。

Ribbon 是 Netflix 发布的负载均衡器 , 它有助于控制 HTTP 和 TCP 客户端的行为. 为 Ribbon 配置服务提供者地址列表后,Ribbon 就可基于某种负载均衡算法,自动帮助服务消费者去请求. Ribbon 默认为我们提供了很多的负载均衡算法,例如轮询,随机等. 当然,我们也可以为 Ribbon 实现自定义的负载均衡算法.

#### 实现架构
![](http://plsbxlixi.bkt.clouddn.com/FvhcWfz-H28TJrVo_nL_QxlW7gCc)

#### 使用 Ribbon
添加依赖：
spring-cloud-starter-netflix-eureka-server 中已经包含了 ribbon，故不需要再重复引入。
![](http://plsbxlixi.bkt.clouddn.com/Fi6dTsZyC9qacHbsU0dEa-doTv20)

在 RestTemplate 设置 @LoadBalanced 注解：

```java
public class OrderApplication {

    @Bean
    @LoadBalanced       //开启负载均衡
    public RestTemplate restTemplate() {
        return new RestTemplate(new OkHttp3ClientHttpRequestFactory());
    }

```
这样，RestTemplate 就具备了负载均衡的功能。

#### 测试负载均衡
启动两个 springcloud-microservice-item（注意修改端口）
![](http://plsbxlixi.bkt.clouddn.com/Flz750EQrlyhmj6p0keSZgNzWAxq)

引入 Spring Boot 单元测试依赖：

```xml
<!-- 添加 Spring Boot 单元测试包-->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
</dependency>
```

编写测试类：

```java

/**
 * 测试负载均衡策略
 */
@RunWith(SpringJUnit4ClassRunner.class)
@SpringBootTest(classes = OrderApplication.class)
public class LoadBalanceTest {

    @Autowired
    private LoadBalancerClient loadBalancerClient;

    @Test
    public void test() {
        String itemServiceId = "springcloud-microservice-item";

        for (int i = 0; i < 50; i++) {
            ServiceInstance serviceInstance = loadBalancerClient.choose(itemServiceId);
            System.out.println("第" + i +"次调用:"
                    + serviceInstance.getHost() +":" + serviceInstance.getPort());
        }
    }
}

```
启动，查看测试结果：
![](http://plsbxlixi.bkt.clouddn.com/FpX7Vx7bdSAg4NxZCnz_DjN6ArSC)
可见 Ribbon 中默认的负载均衡算法是轮询。

如果要设置负载均衡为随机，需要修改配置文件：
在消费端 application.properties 中添加：

```properties
springcloud-microservice-item.ribbon.NFLoadBalancerRuleClassName=com.netflix.loadbalancer.RandomRule
```

再次测试：
![](http://plsbxlixi.bkt.clouddn.com/FsbcY9lf8kWNStPbZNU5SpZJ_Ai2)

可见都是随机调用的了。



**推荐阅读：**

[Spring Cloud 最佳项目构建 ](https://turbobin.github.io/2019/01/10/best-springcloud-practice/)



> 本文首发于 [turbobin's Blog](https://turbobin.github.io/) 。写技术博客不易，转载请注明出处，附上本原文链接， 谢谢合作。