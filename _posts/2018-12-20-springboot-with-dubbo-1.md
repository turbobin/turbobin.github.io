---
layout:     post
title:      Spring Boot 整合 Dubbo 框架(一)
subtitle:   dubbo 注解配置方式
date:       2018-12-20
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
category: 技术
tags:
    - [微服务, spring boot, dubbo]
---

### 简述 ###

在“[基于SpringBoot 整合Mybatis]({{site.url}}/2018/12/17/springboot-with-mybatis/)” 的案例中，把服务的接口、实现类和服务的调用都放在了一起。随着项目的扩展，服务越来越多，显然会不利于项目的维护，因此需要进行模块的拆分，大体可拆分成三个大的模块：服务公共接口、服务提供者（实现类）、服务消费者（调用类）。但是还有一个问题，如果服务部署在多台机器上，服务消费者只能通过ip地址和端口去调用服务，如果服务部署有变更，则需要去修改地址，耦合性太强。因此需要一个注册中心，每个服务都往这个中心注册自己，同时暴露服务接口，服务消费者只需要在注册中心订阅服务，就可以通过远程调用的方式调用服务的功能（RPC），这个过程叫做服务的治理，采用服务的注册与发现机制。Dubbo就是一个专注于RPC的服务治理框架，它的架构图如下：
![]({{site.url}}/images/java/springboot-27.png)

**节点角色说明**
<table>
<thead>
<tr>
<th>节点</th>
<th>角色说明</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>Provider</code></td>
<td>暴露服务的服务提供方</td>
</tr>
<tr>
<td><code>Consumer</code></td>
<td>调用远程服务的服务消费方</td>
</tr>
<tr>
<td><code>Registry</code></td>
<td>服务注册与发现的注册中心</td>
</tr>
<tr>
<td><code>Monitor</code></td>
<td>统计服务的调用次数和调用时间的监控中心</td>
</tr>
<tr>
<td><code>Container</code></td>
<td>服务运行容器</td>
</tr>
</tbody>
</table>

**调用关系说明**

1.	服务容器负责启动，加载，运行服务提供者。
2.	服务提供者在启动时，向注册中心注册自己提供的服务。
3.	服务消费者在启动时，向注册中心订阅自己所需的服务。
4.	注册中心返回服务提供者地址列表给消费者，如果有变更，注册中心将基于长连接推送变更数据给消费者。
5.	服务消费者，从提供者地址列表中，基于软负载均衡算法，选一台提供者进行调用，如果调用失败，再选另一台调用。
6.	服务消费者和提供者，在内存中累计调用次数和调用时间，定时每分钟发送一次统计数据到监控中心。

### Dubbo 项目构建

####  Step1：下载zookeeper ####
Dubbo的注册中心一般使用 zookeeper，也是官方的推荐，可用于生产环境。  
我这里用的是 zookeeper-3.4.12.tar.gz (有较新版本也可下载)  
可以上传Linux解压使用，也可以在 Windows 本地解压做测试使用（依赖JDK启动）。

以 Windows 为例，解压 tar 包，拷贝一份 conf/zoo_sample.cfg，改成zoo.cfg
![]({{site.url}}/images/java/springboot-28.png)
打开zoo.cfg，修改：
![]({{site.url}}/images/java/springboot-29.png)
在根目录下创建data和log目录。

进入bin目录，Windows双击`zkServer.cmd`启动，Linux下使用“`./zkServer.sh start`”启动。

#### Step2：创建maven项目 ####
结构如下：
![]({{site.url}}/images/java/springboot-30.png)

**parent: pom.xml。统一管理依赖版本**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ccb.dubbo</groupId>
    <artifactId>springboot-dubbo-parent</artifactId>
    <packaging>pom</packaging>
    <version>0.0.1-SNAPSHOT</version>
    <name>springboot-dubbo-parent</name>
    <description>Demo project for Spring Boot Dubbo</description>

    <modules>
        <module>springboot-dubbo-common-api</module>
        <module>springboot-dubbo-provider</module>
        <module>springboot-dubbo-consumer</module>
    </modules>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.0.7.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <java.version>1.8</java.version>

        <dubbo.starter.version>0.2.0</dubbo.starter.version>
        <zookeeper.version>3.4.12</zookeeper.version>
        <curator-framework.version>4.0.0</curator-framework.version>
        <pagehelper.start.version>1.2.5</pagehelper.start.version>
        <mybatis.start.version>1.3.2</mybatis.start.version>
        <druid.start.version>1.1.9</druid.start.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-test</artifactId>
                <scope>test</scope>
            </dependency>

            <!-- springboot整合dubbo项目，0.2.0版本结合了spring boot2.0，
            springboot 1.0+ 则使用0.1.0 -->
            <dependency>
                <groupId>com.alibaba.boot</groupId>
                <artifactId>dubbo-spring-boot-starter</artifactId>
                <version>${dubbo.starter.version}</version>
            </dependency>

            <!--Dubbo 上面dubbo-spring-boot-starter已包含dubbo 2.6.2
            若要使用更高版本则加上此依赖-->
            <!--<dependency>-->
                <!--<groupId>com.alibaba</groupId>-->
                <!--<artifactId>dubbo</artifactId>-->
                <!--<version>2.6.5</version>-->
            <!--</dependency>-->
            <!--Spring Context Extras-->
            <!--<dependency>-->
                <!--<groupId>com.alibaba.spring</groupId>-->
                <!--<artifactId>spring-context-support</artifactId>-->
                <!--<version>1.0.2</version>-->
            <!--</dependency>-->

            <!-- 上面dubbo-spring-boot-starter已包含zookeeper 3.4.9，
            若需要更高版本则加上此依赖 -->
            <dependency>
                <groupId>org.apache.zookeeper</groupId>
                <artifactId>zookeeper</artifactId>
                <version>${zookeeper.version}</version>
            </dependency>

            <dependency>
                <groupId>org.apache.curator</groupId>
                <artifactId>curator-framework</artifactId>
                <version>${curator-framework.version}</version>
            </dependency>

            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-web</artifactId>
            </dependency>

            <!-- spring boot整合mybatis-->
            <dependency>
                <groupId>org.mybatis.spring.boot</groupId>
                <artifactId>mybatis-spring-boot-starter</artifactId>
                <version>${mybatis.start.version}</version>
            </dependency>

            <dependency>
                <groupId>mysql</groupId>
                <artifactId>mysql-connector-java</artifactId>
                <scope>runtime</scope>
            </dependency>

            <!-- 分页插件 -->
            <dependency>
                <groupId>com.github.pagehelper</groupId>
                <artifactId>pagehelper-spring-boot-starter</artifactId>
                <version>${pagehelper.start.version}</version>
            </dependency>
            <!-- alibaba的druid数据库连接池 -->
            <dependency>
                <groupId>com.alibaba</groupId>
                <artifactId>druid-spring-boot-starter</artifactId>
                <version>${druid.start.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>

            <!-- mybatis generator 自动生成代码插件 -->
            <plugin>
                <groupId>org.mybatis.generator</groupId>
                <artifactId>mybatis-generator-maven-plugin</artifactId>
                <version>1.3.2</version>
                <configuration>
                    <configurationFile>${basedir}/src/main/resources/generator/generatorConfig.xml</configurationFile>
                    <overwrite>true</overwrite>
                    <verbose>true</verbose>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>

```

#### Step3：公共接口 ####

存放User实体类和UserService接口
![]({{site.url}}/images/java/springboot-31.png)

**common-api: pom.xml**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springboot-dubbo-parent</artifactId>
        <groupId>com.ccb.dubbo</groupId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springboot-dubbo-common-api</artifactId>

</project>

```

**User:**

```java
public class User implements Serializable {

    private static final long serialVersionUID = 1L; //需要实现序列化

    private Integer id;

    private String username;

    private String password;

    private String email;

    private String sex;

    private Integer age;

    private String city;

	//省略getter、setter和构造方法
}


```

**UserService：**

```java

/**
 * 用户业务层增删改查接口
 */
public interface UserService {

    String sayHello(String name);

    int addUser(User user);

    User findUserById(Integer userId);

    List<User> findAllUsers();      //一会在UserMapper.xml中添加这个方法

    int updateUser(User user);

    int deleteUserById(Integer userId);
}

```

#### Step4：服务提供者 ####

![]({{site.url}}/images/java/springboot-32.png)

Mapper的生成参考“[基于Spring Boot整合Mybatis，与数据库交互]({{site.url}}/2018/12/17/springboot-with-mybatis/)”一节，注意把User实体生成到`com.ccb.dubbo.common.model`中( generatorConfig.xml 中使用绝对路径指定目录)。

把 common-api 依赖进来：

**pom.xml**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springboot-dubbo-parent</artifactId>
        <groupId>com.ccb.dubbo</groupId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springboot-dubbo-provider</artifactId>
    <dependencies>
        <dependency>
            <groupId>com.ccb.dubbo</groupId>
            <artifactId>springboot-dubbo-common-api</artifactId>
            <version>0.0.1-SNAPSHOT</version>
        </dependency>

        <dependency>
            <groupId>com.alibaba.boot</groupId>
            <artifactId>dubbo-spring-boot-starter</artifactId>
        </dependency>

        <dependency>
            <groupId>org.apache.curator</groupId>
            <artifactId>curator-framework</artifactId>
        </dependency>

        <dependency>
            <groupId>org.apache.zookeeper</groupId>
            <artifactId>zookeeper</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>2.0.7.RELEASE</version>
        </dependency>

        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
        </dependency>

        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>5.1.34</version>
        </dependency>

        <!-- alibaba的druid数据库连接池 -->
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid-spring-boot-starter</artifactId>
        </dependency>

        <!-- 分页插件 -->
        <dependency>
            <groupId>com.github.pagehelper</groupId>
            <artifactId>pagehelper-spring-boot-starter</artifactId>
        </dependency>

    </dependencies>

</project>

```

**UserMapper:**

```java

@Mapper
@Component
public interface UserMapper {
    int deleteByPrimaryKey(Integer id);

    int insert(User record);

    int insertSelective(User record);

    User selectByPrimaryKey(Integer id);

    int updateByPrimaryKeySelective(User record);

    int updateByPrimaryKey(User record);

    List<User> selectAllUsers();    //需要在UserMapper.xml中添加
}

```

**UserServiceImpl**  
注意这里使用`@Service` 用的是 dubbo 提供的注解：

```java

import com.alibaba.dubbo.config.annotation.Service;

@Service(version = "1.0.0")
public class UserServiceImpl implements UserService {

    @Autowired
    private UserMapper userMapper;

    @Override
    public String sayHello(String name) {
        return "Hello, " + name;
    }

    @Override
    public int addUser(User user) {
        return userMapper.insert(user);
    }

    @Override
    public User findUserById(Integer userId) {
        return userMapper.selectByPrimaryKey(userId);
    }

    @Override
    public List<User> findAllUsers() {
        return userMapper.selectAllUsers();
    }

    @Override
    public int updateUser(User user) {
        return userMapper.updateByPrimaryKey(user);
    }

    @Override
    public int deleteUserById(Integer userId) {
        return userMapper.deleteByPrimaryKey(userId);
    }
}

```

**启动类：**

```java
@EnableDubbo	//标注启用dubbo
@SpringBootApplication
//@ComponentScan(basePackages = {"com.ccb.dubbo.provider.mapper"})
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

}
```

**配置文件 application.properties**

```properties
spring.application.name=springboot-dubbo-provider
##端口号
server.port=8880


## Dubbo 服务提供者配置
dubbo.application.name=spring-dubbo-provider
dubbo.registry.address=zookeeper://127.0.0.1:2181
dubbo.protocol.name=dubbo
dubbo.protocol.port=20880
dubbo.monitor.protocol=registry
#dubbo.scan.basePackages=com.ccb.dubbo.service

# druid 连接池配置

# 基本属性
spring.datasource.name=mysql
spring.datasource.type=com.alibaba.druid.pool.DruidDataSource
spring.datasource.druid.filters=stat
spring.datasource.druid.driver-class-name=com.mysql.jdbc.Driver
spring.datasource.druid.url=jdbc:mysql://127.0.0.1:3306/mydatabase?useUnicode=true&characterEncoding=UTF-8&allowMultiQueries=true
spring.datasource.druid.username=root
spring.datasource.druid.password=root
#配置初始化大小/最小/最大
spring.datasource.druid.initial-size=1
spring.datasource.druid.min-idle=1
spring.datasource.druid.max-active=20
#获取连接等待超时时间
spring.datasource.druid.max-wait=60000
#间隔多久进行一次检测，检测需要关闭的空闲连接
spring.datasource.druid.time-between-eviction-runs-millis=60000
#一个连接在池中最小生存的时间
spring.datasource.druid.min-evictable-idle-time-millis=300000
spring.datasource.druid.validation-query=SELECT 'x'
spring.datasource.druid.test-while-idle=true
spring.datasource.druid.test-on-borrow=false
spring.datasource.druid.test-on-return=false
#打开PSCache，并指定每个连接上PSCache的大小。oracle设为true，mysql设为false。分库分表较多推荐设置为false
spring.datasource.druid.pool-prepared-statements=false
spring.datasource.druid.max-pool-prepared-statement-per-connection-size=20

#mybatis配置
mybatis.mapper-locations=classpath:mapping/*.xml
mybatis.type-aliases-package=com.ccb.dubbo.common.model

```

#### Step5：服务消费者 ####
![]({{site.url}}/images/java/springboot-33.png)

**pom.xml**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springboot-dubbo-parent</artifactId>
        <groupId>com.ccb.dubbo</groupId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springboot-dubbo-consumer</artifactId>
    <dependencies>
        <dependency>
            <groupId>com.ccb.dubbo</groupId>
            <artifactId>springboot-dubbo-common-api</artifactId>
            <version>0.0.1-SNAPSHOT</version>
        </dependency>

        <dependency>
            <groupId>com.alibaba.boot</groupId>
            <artifactId>dubbo-spring-boot-starter</artifactId>
        </dependency>

        <dependency>
            <groupId>org.apache.curator</groupId>
            <artifactId>curator-framework</artifactId>
        </dependency>

        <dependency>
            <groupId>org.apache.zookeeper</groupId>
            <artifactId>zookeeper</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>2.0.7.RELEASE</version>
        </dependency>
    </dependencies>

</project>

```

**UserController**  
使用`@Reference`把服务接口注进来

```java

import com.alibaba.dubbo.config.annotation.Reference;

@RestController
@RequestMapping(value = "user")
public class UserController {

    @Reference(version = "1.0.0")   //引用服务接口
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

**配置文件application.properties**

```properties
spring.application.name=springboot-dubbo-consumer
##端口号
server.port=8881

## Dubbo 服务提供者配置
dubbo.application.name=spring-dubbo-consumer
dubbo.registry.address=zookeeper://127.0.0.1:2181
dubbo.protocol.name=dubbo
dubbo.protocol.port=20880
dubbo.monitor.protocol=registry
#dubbo.scan.basePackages=com.ccb.dubbo.consumer.controller

```

**启动类，这里测试了是否能调用 userSerivce 方法**

```java

@EnableDubbo
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
//        SpringApplication.run(Application.class, args);
        ConfigurableApplicationContext run = SpringApplication.run(Application.class, args);
        UserController bean = run.getBean(UserController.class);
        System.out.println(bean.userService.sayHello("turbobin"));

    }
}

```

#### Step6: 测试 ####

下面分别启动服务提供者和服务消费者（检查是否先启动了zookeeper）
![]({{site.url}}/images/java/springboot-34.png)

可见，调用成功了。

在浏览器中测试：
![]({{site.url}}/images/java/springboot-35.png)
![]({{site.url}}/images/java/springboot-36.png)
![]({{site.url}}/images/java/springboot-37.png)

测试成功。

#### 小结 ####
通过这个案例，现在有点微服务的概念了，按我的理解，微服务的基本思想其实就是把一个大的功能拆分成一个个微小的服务，每个服务可以单独维护，服务提供者只需要向注册中心注册，同时对外暴露接口，服务消费者通过向注册中心订阅服务，就可以实现远程调用服务了，实现了服务的治理。当然，微服务中还有负载均衡、容错保护、配置中心等功能，后面用到Spring Cloud的时候再来实现。



**推荐阅读：**

[基于Spring Boot整合Mybatis，与数据库交互]({{site.url}}/2018/12/17/springboot-with-mybatis/)

[Spring Boot 整合 Dubbo 框架(二) - dubbo xml 配置方式]({{site.url}}/2018/12/21/springboot-with-dubbo-2/)




>写技术博客不易，转载请注明出处，附上原文链接[https://turbobin.github.io/](https://turbobin.github.io/) , 谢谢合作。