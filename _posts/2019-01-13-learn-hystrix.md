---
layout:     post
title:      容错保护机制：Hystrix
subtitle:   
date:       2019-01-13
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
category: 技术
tags:

   - [微服务, spring cloud]

---

#### 问题分析
举个例子， 在一个电商网站中，我们可能会将系统拆分成用户、订单、库存、积分、评论等一系列的服务单元。 用户创建一个订单的时候，客户端将调用订单服务的创建订单接口，此时创建订单接口又会向库存服务请求出货 (判断是否有足够库存来出货)。此时若库存服务因自身处理逻辑等原因造成响应缓慢，会直接导致创建订单服务的线程被挂起，以等待库存申请服务的响应， 在漫长的等待之后用户会因为请求库存失败而得到创建订单失败的结果。 如果在高并发情况下之下， 因这些挂起的线程在等待库存服务的响应而未能释放，使得后续到来的创建订单请求被阻塞，最终导致订单服务不可用。

在微服务架构中，存在这么多的服务单元，若一个单元出现故障，就很容易因依赖关系引发故障蔓延，最终导致整个系统瘫痪， 这种现象被称之为为雪崩效应。服务雪崩效应是一种因“服务提供者”的不可用导致“服务消费者”的不可用，并将不可用逐渐放大的过程。

如下图所示：A 作为服务提供者，B 为 A 的服务消费者，C 和 D 是 B 的服务消费者。A 不可用引起了 B 的不可用，并将不可用像滚雪球一样放大到 C 和 D 时，雪崩效应就形成了。
![](http://plsbxlixi.bkt.clouddn.com/FiVMYQNFyqMvNwbq9msy0G-BbsUr)

这样的架构相交于传统架构更加的不稳定. 为了解决这样的问题，就产生了断路器等一系列的服务保护机制.

针对上述问题，Spring Cloud Hystrix 实现了断路器 ， 线程隔离等一系列服务保护功能. 它也是基于 Netfilx 的开源框架 Hystrix 实现的. 该框架的目标在于通过控制那些访问远程系统 ， 服务和第三方库的节点 ， 从而对延迟和故障提供更强大的容错能力. Hystrix 具备服务降级 ， 服务熔断 ， 线程和信号隔离 ， 请求缓存， 请求合并以及服务监控的强大功能.

#### Hystrix 简介
目前 Hystrix 项目也在 github 上托管: [https://github.com/Netflix/Hystrix/](https://github.com/Netflix/Hystrix/)
![](http://plsbxlixi.bkt.clouddn.com/FvMBYSE5yHNg6SFv8C_R9WPWkff9)
Hystrix 是由 Netflix 开源的一个延迟和容错库，用于隔离访问远程系统，服务或者第三方库，防止级联失败， 在复杂的分布式系统中实现恢复能力，从而提升系统的可用性和容错性. Hystrix 主要通过以下几点实现延迟和容错:

* **包裹请求**: 使用 HystrixCommand 包裹对依赖的调用逻辑 ， 每一个命令在独立的线程中执行. 
* **跳闸机制**: 当某服务的错误率超过一定阀值时 ， Hystrix 可以自动或者手动跳闸， 停止请求该服务一段时间
* **资源隔离**:  Hystrix 为每个依赖都维护了一个小型的线程池 ， 如果该线程池已满 ， 发往该依赖的请求就会被立即拒绝， 从而加上失败判定
* **监控**: Hystrix 可以几乎实时的监控运行指标和配置的变化， 例如成功 ， 失败 ， 超时 以及被拒绝的请求等
* **回退机制**: 当请求失败，超时，被拒绝， 或当断路器打开是 ， 执行回退逻辑. 回退逻辑可有开发人员自行提供，例如返回一个缺省值

#### 原理说明
正常请求:

![](http://plsbxlixi.bkt.clouddn.com/Ft0c7KaJOyiTOpG35TqcMs7txZAT)

当对特定服务的呼叫达到一定阈值时（Hystrix 中的默认值为 5 秒内的 20 次故障），电路打开，不进行通讯。并且是一个隔离的线程中进行的。

![](http://plsbxlixi.bkt.clouddn.com/FmwUVSIYTHqMNJvSZKCwRIhku6ES)

#### 快速入门

参看上一节：[Spring Cloud 最佳项目构建](https://turbobin.github.io/2019/01/10/best-springcloud-practice/)

在服务消费端（springcloud-microservice-eureka）增加 Hystrix 实现容错。
在 service-impl 模块 pom.xml 中导入依赖：

```xml
<!-- 加入 hystrix 的依赖 -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-hystrix</artifactId>
</dependency>

```
只需要修改 ItemServiceRemote：

```java
// 查询商品列表
    @HystrixCommand(fallbackMethod = "queryItemByIdFallbackMethod")    // 进行容错处理
    Item queryItemById(Integer itemId) {
        // 使用 HttpClient 工具发送请求获取商品的数据
        // 我们也可以使用 spring 给我们提供的另个一个类 RestTemplate,来发送 Http 请求
        String itemServiceId = "springcloud-microservice-item";

        //服务发现，返回实例
//        List<ServiceInstance> instances =
//                discoveryClient.getInstances(itemServiceId);
//
//        if (instances == null || instances.isEmpty()) {
//            return null;
//        }
//
//        ServiceInstance instance = instances.get(0);
//        String url = "http://" + instance.getHost()
//                + ":" +instance.getPort() + "/item/";
//        System.out.println("url = [" + url + itemId + "]");
//        Item item = restTemplate.getForObject(url + itemId, Item.class);
//
//        // 返回
//        return item;
        
        //实现容错后，查询可以变得更简单
        return restTemplate.getForObject("http://" + itemServiceId + "/item/" + itemId, Item.class);

    }

    /**
     * 断路返回方法
     * @param itemId
     * @return
     */
    private Item queryItemByIdFallbackMethod(Integer itemId) {
        return new Item(itemId, "查询商品信息出错！", null, null, null);
    }

```
修改启动类，加入断路器注解 `@EnableHystrix`
```java

@EnableHystrix              // 开启容错机制
@EnableDiscoveryClient      // 声明这是 Eureka 的客户端
@ComponentScan(basePackages = {"com.ccb.springcloud.comsumer"})
@MapperScan(basePackages = {"com.ccb.springcloud.comsumer.common.mapper"})
@SpringBootApplication
public class OrderApplication {

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate(new OkHttp3ClientHttpRequestFactory());
    }

    public static void main(String[] args) {
        SpringApplication.run(OrderApplication.class, args);
    }
}

```
重启测试
先测试正常数据：
![](http://plsbxlixi.bkt.clouddn.com/FikygNO_Gfoiu_YdRgAx-ixVz9yT)
把 ItemApplication 停掉，再次测试：
![](http://plsbxlixi.bkt.clouddn.com/FtNemzj9Bjd1Hv4ccpAckSL5Eoaf)
返回了自定义的友好信息。

#### 需注意的问题：
`@HystrixCommand` 注解必须加在 Service 类的一级方法上才能生效，加在内部调用的方法上是无效的。
举个栗子：

```java

@Service
public class HelloService {
    @Autowired
    private RestTemplate restTemplate;

    @HystrixCommand(fallbackMethod = "helloError")      // 必须加在一级方法上
    public String hello() {
        return sayHello();
//        String string = restTemplate.getForObject("httpa://HELLO-SERVICE/hello", String.class);
//        System.out.println("string:" + string);
//        return string;
    }

//    @HystrixCommand(fallbackMethod = "helloError")  // 加在这里不会起作用
    private String sayHello() {
        String string = restTemplate.getForObject("httpa://HELLO-SERVICE/hello", String.class);
        System.out.println("string:" + string);
        return string;
    }

    public String helloError() {
        return "服务故障了";
    }
}

```
Controller：

```java
@Autowired
private HelloService helloService;

@GetMapping(value = "hello")
public String hello() {
    return helloService.hello();
}
```



**推荐阅读：**

[Spring Cloud 最佳项目构建 ](https://turbobin.github.io/2019/01/10/best-springcloud-practice/)

[Spring Cloud 及 Eureka 注册中心](https://turbobin.github.io/2019/01/07/springcloud-and-eureka/)



> 本文首发于 [turbobin's Blog](https://turbobin.github.io/) 。转载请注明出处，附上本原文链接， 谢谢合作。