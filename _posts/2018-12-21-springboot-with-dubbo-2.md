---
layout:     post
title:      Spring Boot 整合 Dubbo 框架(二)
subtitle:   dubbo xml 配置方式
date:       2018-12-21
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
category: 技术
tags:
    - [微服务, spring boot, dubbo]
---

上一节用到的是注解的方式来构建 dubbo 项目，当接口服务越来越多，希望更直观的管理服务接口时，一般使用xml方式配置比较好。

dubbo加载配置的优先顺序为：  
系统属性 > dubbo.properties > XML/Spring-boot自动装配方式。

说两种情况：

① 如果公共配置很简单，没有多注册中心，多协议等情况，或者想多个 Spring 容器共享配置，可以使用 dubbo.properties 作为缺省配置。  
Dubbo 将自动加载 classpath 根目录下的 dubbo.properties，可以通过JVM启动参数
`-Ddubbo.properties.file=xxx.properties` 改变缺省配置位置。

下面来改造上一节的配置：

**服务提供者 springboot-dubbo-provider：**

在 application.properties同级目录下新建一个dubbo.properties，将application.properties 中 dubbo 的相关配置移到 dubbo.propertie中：

```properties
## Dubbo 服务提供者配置
dubbo.application.name=spring-dubbo-provider
dubbo.registry.address=zookeeper://127.0.0.1:2181
dubbo.protocol.name=dubbo
dubbo.protocol.port=20880
dubbo.monitor.protocol=registry
# 将扫描接口的配置放到xml中
#dubbo.scan.basePackages=com.ccb.dubbo.common.service
```

在 `src/main/resources`下新建 `dubbo/dubbo-provider.xml`，内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:dubbo="http://dubbo.apache.org/schema/dubbo"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans-4.3.xsd
       http://dubbo.apache.org/schema/dubbo
       http://dubbo.apache.org/schema/dubbo/dubbo.xsd">

    <!--声明需要暴露的服务接口, ref表明注册的接口实现类@Service指定的bean名称-->
    <dubbo:service interface="com.ccb.dubbo.common.service.UserService" 
                   ref="userService" />

</beans>

```

UserServiceImpl修改注解:  
现在不能使用dubbo的`@Service`注解了，需要改为原来使用 spring 的注解，并且这里需要写上name `“userService”`，否则会报 `not defined bean “userService”`，这里遇到很大的坑。

```java
//import com.alibaba.dubbo.config.annotation.Service;
import org.springframework.stereotype.Service;

//@Service(version = "1.0.0")
@Service("userService")
public class UserServiceImpl implements UserService {

```

最后修改启动类，把xml配置导入进来：

```java

//@EnableDubbo  //注释，改用xml加载
@SpringBootApplication
@ImportResource(value = {"classpath:dubbo/*.xml"})
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

}

```

服务提供者就修改完成了，启动试一下：
![]({{site.url}}/images/java/springboot-38.png)
如果出现了zookeeper相关信息，一般就表示注册没问题。

**服务消费者 springboot-dubbo-consumer：**

与服务提供者差不多，将 application.properties 中 dubbo 配置放到 dubbo.properties中（也可以不分离，不是强制要求）

```

## Dubbo 服务消费者配置
dubbo.application.name=spring-dubbo-consumer
dubbo.registry.address=zookeeper://127.0.0.1:2181
dubbo.protocol.name=dubbo
dubbo.protocol.port=20880
dubbo.monitor.protocol=registry
# 在xml中配置消费接口
#dubbo.scan.basePackages=com.ccb.dubbo.consumer.controller

```

在 `src/main/resources`下新建 `dubbo/dubbo-consumer.xml`，内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:dubbo="http://dubbo.apache.org/schema/dubbo"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans-4.3.xsd
       http://dubbo.apache.org/schema/dubbo
       http://dubbo.apache.org/schema/dubbo/dubbo.xsd">

    <!-- 生成远程服务代理，可以和本地bean一样使用userService -->
    <dubbo:reference id="userService" 
                     interface="com.ccb.dubbo.common.service.UserService" />
</beans>

```

修改 UserController，这里不再使用`@Reference`注入：

```java

@RestController
@RequestMapping(value = "user")
public class UserController {

//  @Reference(version = "1.0.0")   //注释，采用xml配合spring注解方式注入
    @Autowired(required = false)
    public UserService userService;

    @RequestMapping(value = "/all")
    public Object findAllUsers(){
        return userService.findAllUsers();
    }

    @RequestMapping(value = "/{id}")
    public Object findUserById(@PathVariable("id") Integer userId){
        return userService.findUserById(userId);
    }

    @RequestMapping("/sayHello/{name}")
    public String sayHello(@PathVariable("name") String name) {
        return userService.sayHello(name);
    }


}

```
修改启动类：

```java

//@EnableDubbo  //注释，改用xml加载
@SpringBootApplication
@ImportResource(value = {"classpath:dubbo/*.xml"})
public class Application {

    public static void main(String[] args) {
//        SpringApplication.run(Application.class, args);
        ConfigurableApplicationContext run = SpringApplication.run(Application.class, args);
        UserController bean = run.getBean(UserController.class);
        System.out.println(bean.userService.sayHello("turbobin"));

    }

}

```

启动测试：
![]({{site.url}}/images/java/springboot-39.png)
![]({{site.url}}/images/java/springboot-40.png)
可以看到，调用成功了。

② 在dubbo官方文档的推荐用法中，其实不推荐使用dubbo.properties，而推荐使用对应的xml配置：

**dubbo.properties 中属性名与 XML 的对应关系**

<ol>
<li>
<p>应用名 <code>dubbo.application.name</code></p>
<pre><code class="highlight"><span class="hljs-tag">&lt;<span class="hljs-name">dubbo:application</span> <span class="hljs-attr">name</span>=<span class="hljs-string">"myalibaba"</span> &gt;</span>
</code></pre>
</li>
<li>
<p>注册中心地址 <code>dubbo.registry.address</code></p>
<pre><code class="highlight"><span class="hljs-tag">&lt;<span class="hljs-name">dubbo:registry</span> <span class="hljs-attr">address</span>=<span class="hljs-string">"11.22.33.44:9090"</span> &gt;</span>
</code></pre>
</li>
<li>
<p>调用超时 <code>dubbo.service.*.timeout</code></p>
<p>可以在多个配置项设置超时 <code>timeout</code>，由上至下覆盖（即上面的优先）<sup class="footnote-ref"><a href="#fn5" id="fnref5">[5]</a></sup>，其它的参数（<code>retries</code>、<code>loadbalance</code>、<code>actives</code>等）的覆盖策略与 <code>timeout</code> 相同。示例如下：</p>
<p>提供者端特定方法的配置</p>
<pre><code class="highlight"><span class="hljs-tag">&lt;<span class="hljs-name">dubbo:service</span> <span class="hljs-attr">interface</span>=<span class="hljs-string">"com.alibaba.xxx.XxxService"</span> &gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">dubbo:method</span> <span class="hljs-attr">name</span>=<span class="hljs-string">"findPerson"</span> <span class="hljs-attr">timeout</span>=<span class="hljs-string">"1000"</span> /&gt;</span>
<span class="hljs-tag">&lt;/<span class="hljs-name">dubbo:service</span>&gt;</span>
</code></pre>
<p>提供者端特定接口的配置</p>
<pre><code class="highlight"><span class="hljs-tag">&lt;<span class="hljs-name">dubbo:service</span> <span class="hljs-attr">interface</span>=<span class="hljs-string">"com.alibaba.xxx.XxxService"</span> <span class="hljs-attr">timeout</span>=<span class="hljs-string">"200"</span> /&gt;</span>
</code></pre>
</li>
<li>
<p>服务提供者协议 <code>dubbo.service.protocol</code>、服务的监听端口 <code>dubbo.service.server.port</code></p>
<pre><code class="highlight"><span class="hljs-tag">&lt;<span class="hljs-name">dubbo:protocol</span> <span class="hljs-attr">name</span>=<span class="hljs-string">"dubbo"</span> <span class="hljs-attr">port</span>=<span class="hljs-string">"20880"</span> /&gt;</span>
</code></pre>
</li>
<li>
<p>服务线程池大小 <code>dubbo.service.max.thread.threads.size</code></p>
<pre><code class="highlight"><span class="hljs-tag">&lt;<span class="hljs-name">dubbo:protocol</span> <span class="hljs-attr">threads</span>=<span class="hljs-string">"100"</span> /&gt;</span>
</code></pre>
</li>
<li>
<p>消费者启动时，没有提供者是否抛异常 <code>alibaba.intl.commons.dubbo.service.allow.no.provider</code></p>
<pre><code class="highlight"><span class="hljs-tag">&lt;<span class="hljs-name">dubbo:reference</span> <span class="hljs-attr">interface</span>=<span class="hljs-string">"com.alibaba.xxx.XxxService"</span> <span class="hljs-attr">check</span>=<span class="hljs-string">"false"</span> /&gt;</span>
</code></pre>
</li>
</ol>



**推荐阅读：**

[Spring Boot 整合 Dubbo 框架(一) - dubbo 注解配置方式]({{site.url}}/2018/12/20/springboot-with-dubbo-1/)


>写技术博客不易，转载请注明出处，附上原文链接[https://turbobin.github.io/](https://turbobin.github.io/) , 谢谢合作。