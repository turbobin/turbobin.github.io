---
layout:     post
title:      Spring Cloud 最佳项目构建
subtitle:   
date:       2019-01-10
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
category: 技术
tags:

   - [微服务, spring cloud]

---

### 可能是最佳的微服务项目结构实践

实际项目开发中经常使用 maven 聚合项目来进行构建，为了保持相对独立性，可按照分层逻辑把各个逻辑层拆开，参考如下：
![](http://plsbxlixi.bkt.clouddn.com/Ft90tmHTifdODHPJT-kaALOCdqTD)

首先分成三大类：

- 服务提供者 (springcloud-microservice-provider)
- 服务消费者 (springcloud-microservice-comsumer)
- 注册中心 (springcloud-microservice-eureka)

IEDA 可通过 Ctrl+Alt+Shift+s (或选择 file ->Project Structure) 打开项目构建，选择 Modules，点击 + ->New Project 创建三个模块，这样就可以将像 eclipse 一样将项目显示在同一个窗口中。

服务提供者和服务消费者内部结构类似，可分为：

- 父类 pom.xml：同一管理子项目依赖包版本
- app：存放启动类和公共配置文件
- common-api：存放公共接口，如实体类 model，持久层数据访问对象接口 DAO 等
- service-inf：存放业务层接口
- service-impl：存放业务层接口实现类
  子模块之间如果有调用关系就把相应的子模块依赖进来，但是注意不要循环依赖。

### Spring Cloud 项目构建

下面来用最佳项目结构来构建基本的 Spring Cloud 项目。
结构图如下：
 ![](http://plsbxlixi.bkt.clouddn.com/FlPgmj7qnIuj3CQ-Z2rfID4eIzR_)

#### 注册中心 (springcloud-microservice-eureka)

pom.xml 中导入相应的依赖：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ccb.springcloud.eureka</groupId>
    <artifactId>springcloud-microservice-eureka</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <java.version>1.8</java.version>
        <!--springboot 2.0.x 使用 Finchley.SR2 版本-->
        <spring-cloud.version>Finchley.SR2</spring-cloud.version>
    </properties>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.0.7.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>

    <dependencyManagement>
        <dependencies>
            <!--<导入 spring cloud 依赖管理 >-->
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <!--导入 Eureka 服务的依赖-->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
        </dependency>
    </dependencies>
</project>
```

创建 Eureka 服务端启动类：

```java
package com.ccb.springcloud.eureka;


import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

@EnableEurekaServer         //申明这是一个 Eureka 服务
@SpringBootApplication
public class EurekaServer {

    public static void main(String[] args) {
        SpringApplication.run(EurekaServer.class, args);
    }
}
```

配置文件 application.properties：

```
# 服务端口号  
server.port=6868

# 应用名称  
spring.application.name=springcloud-microserice-eureka:6868
# 是否需要将自己注册到注册中心中,因为本身就是一个注册中心,所以不需要将自己注册到注册中心中  
# 搭建集群时，改为 true  
eureka.client.registerWithEureka=false

# 是否从注册中心中获取注册信息  
eureka.client.fetchRegistry=false

# 客户端和服务端进行交互的地址  
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:6868/eureka/
```

启动 EurekaService，访问 http://localhost:6868/
![](http://plsbxlixi.bkt.clouddn.com/FqDtjSTmkxL7TOL0JEo1ySCQF6cw)

#### 数据准备

**1. 商品库表：**

```sql
CREATE TABLE `items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(50) DEFAULT NULL,
  `picture` varchar(100) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

```

> 注：这里建表的时候千万不要把表字段命名成 sql 关键字，比如：desc，describe，change，alter 等，否则，mapper 里面自动生成的 sql 语句执行会有很大的坑。

插入一些数据：
![](http://plsbxlixi.bkt.clouddn.com/FhC3rBdQND-03z8TbyMqNNrpvyS5)
**2. 创建订单库表**

```sql
CREATE TABLE `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `user_name` varchar(50) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
```

插入一些数据：
![](http://plsbxlixi.bkt.clouddn.com/FngyvvBuDliBhEU5b4DmE_CKDfTx)

**3. 订单详情：**

```sql
CREATE TABLE `order_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) DEFAULT NULL,
  `item_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
```

关联订单和商品数据：
![](http://plsbxlixi.bkt.clouddn.com/FqVtQsqEE0qgM4zn4QVZeWrvbJH9)

#### 服务提供者 (springcloud-microservice-provider)

**1. 父 pom.xml:管理依赖**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ccb.springcloud.provider</groupId>
    <artifactId>springcloud-microservice-provider</artifactId>
    <packaging>pom</packaging>
    <version>1.0.0-SNAPSHOT</version>
    <modules>
        <module>springcloud-microservice-provider-app</module>
        <module>springcloud-microservice-provider-common-api</module>
        <module>springcloud-microservice-provider-service-inf</module>
        <module>springcloud-microservice-provider-service-impl</module>
    </modules>
    <name>springcloud-microservice-provider</name>
    <description>Demo project for Spring Cloud</description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.0.7.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>

    <properties>
        <java.version>1.8</java.version>
        <!--springboot 2.0.x 使用 Finchley.SR2 版本-->
        <spring-cloud.version>Finchley.SR2</spring-cloud.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <!--<导入 spring cloud 依赖管理 >-->
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <dependency>
                <groupId>org.mybatis.spring.boot</groupId>
                <artifactId>mybatis-spring-boot-starter</artifactId>
                <version>1.3.2</version>
            </dependency>

            <dependency>
                <groupId>com.alibaba</groupId>
                <artifactId>druid-spring-boot-starter</artifactId>
                <version>1.1.9</version>
            </dependency>

            <dependency>
                <groupId>mysql</groupId>
                <artifactId>mysql-connector-java</artifactId>
                <version>5.1.47</version>
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

**2. common-api：使用插件自动创建 items 表实体类和 mapper 类**
pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springcloud-microservice-provider</artifactId>
        <groupId>com.ccb.springcloud.provider</groupId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springcloud-microservice-provider-common-api</artifactId>

</project>

```

① 在 resource 下创建 generator/generatorConfig.xml，内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE generatorConfiguration PUBLIC
      "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"
      "http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd">
<generatorConfiguration>
   <!-- 数据库驱动包位置 -->
   <classPathEntry
         location="D:\Maven\.m2\repository\mysql\mysql-connector-java\5.1.47\mysql-connector-java-5.1.47.jar" />
   <!-- <classPathEntry location="C:\oracle\product\10.2.0\db_1\jdbc\lib\ojdbc14.jar" 
      /> -->
   <context id="MySqlTables" targetRuntime="MyBatis3">
      <commentGenerator>
         <property name="suppressAllComments" value="true" />
      </commentGenerator>
      <!-- 数据库链接 URL、用户名、密码 -->
      <jdbcConnection driverClass="com.mysql.jdbc.Driver"
                  connectionURL="jdbc:mysql://localhost:3306/mydatabase" userId="root"
                  password="root">
         <!--<jdbcConnection driverClass="oracle.jdbc.driver.OracleDriver" connectionURL="jdbc:oracle:thin:@localhost:1521:orcl" 
            userId="msa" password="msa"> -->
      </jdbcConnection>
      <javaTypeResolver>
         <property name="forceBigDecimals" value="false" />
      </javaTypeResolver>
      <!-- 生成实体类的包名和位置，这里配置将生成的实体类放在 com.ccb.springcloud.provider.common.model 这个包下 -->
      <javaModelGenerator targetPackage="com.ccb.springcloud.provider.common.model"
                     targetProject="src/main/java">
         <property name="enableSubPackages" value="true" />
         <property name="trimStrings" value="true" />
      </javaModelGenerator>
      <!-- 生成的 SQL 映射文件包名和位置，这里配置将生成的 SQL 映射文件放在 src/main/resources 的 mapping 下 -->
      <sqlMapGenerator targetPackage="mapping"
                   targetProject="src/main/resources">
         <property name="enableSubPackages" value="true" />
      </sqlMapGenerator>
      <!-- 生成 DAO 的包名和位置，这里配置将生成的 dao 类放在 com.ccb.springcloud.provider.common.mapper 这个包下 -->
      <javaClientGenerator type="XMLMAPPER"
                      targetPackage="com.ccb.springcloud.provider.common.mapper" targetProject="src/main/java">
         <property name="enableSubPackages" value="true" />
      </javaClientGenerator>
      <!-- 要生成那些表 (更改 tableName 和 domainObjectName 就可以) -->
      <table tableName="items" domainObjectName="Item"
            enableCountByExample="false" enableUpdateByExample="false"
            enableDeleteByExample="false" enableSelectByExample="false"
            selectByExampleQueryId="false" />
   </context>
</generatorConfiguration>


```

② 点击工具栏上的 Run——EditConfigrations,点+，选择 maven
![](http://plsbxlixi.bkt.clouddn.com/FqDWsFjjDuE-egYCb48WbIdLqrlV)
③ 选择名称，点击运行：
![](http://plsbxlixi.bkt.clouddn.com/Ftnu8Xxulv9Jtw0vgJJGhTzqlh9E)
运行成功后生成了 Item.java，ItemMapper.java，ItemMapper.xml
**3. service-inf：把 common-api 依赖进来**
① pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springcloud-microservice-provider</artifactId>
        <groupId>com.ccb.springcloud.provider</groupId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springcloud-microservice-provider-service-inf</artifactId>

    <!-- 把公共接口依赖进来 -->
    <dependencies>
        <dependency>
            <groupId>com.ccb.springcloud.provider</groupId>
            <artifactId>springcloud-microservice-provider-common-api</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>
    </dependencies>
</project>


```

② 创建 ItemService：

```java
package com.ccb.springcloud.provider.service;

import com.ccb.springcloud.provider.common.model.Item;

public interface ItemService {

    /**
     * 模拟实现商品查询
     */
    Item queryItemById(Integer id);
}


```

**4. service-impl：把 service-inf 依赖进来**
① pom.xml:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springcloud-microservice-provider</artifactId>
        <groupId>com.ccb.springcloud.provider</groupId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springcloud-microservice-provider-service-impl</artifactId>

    <!-- 把 service 接口依赖进来,commmon-api 已在 service-inf 中引入，不需要重复依赖 -->
    <dependencies>
        <dependency>
            <groupId>com.ccb.springcloud.provider</groupId>
            <artifactId>springcloud-microservice-provider-service-inf</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>

        <!-- 加入 spring boot 支持，否则无法引入 spring 注解 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>

        <!-- 加入 web 支持，为了稍后创建一个 controller 类方便直接测试 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

    </dependencies>
</project>


```

② 创建 ItemServiceImpl

这里可以直接导入 common-api 中的包，为什么呢？  
这是因为 maven 的可传递性依赖。比如 C 依赖 B，B 依赖 A，那么 C 可以同时使用 B 和 A 中的包。

```java
package com.ccb.springcloud.provider.service.impl;

import com.ccb.springcloud.provider.common.mapper.ItemMapper;
import com.ccb.springcloud.provider.common.model.Item;
import com.ccb.springcloud.provider.service.ItemService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class ItemServiceImpl implements ItemService {

    @Autowired
    private ItemMapper itemMapper;

    @Override
    public Item queryItemById(Integer id) {
        return itemMapper.selectByPrimaryKey(id);
    }
}

```

③ 创建一个 Controller 来调用：

```java
package com.ccb.springcloud.provider.service.controller;

import com.ccb.springcloud.provider.service.ItemService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("item")
public class ItemController {

    @Autowired
    private ItemService itemService;

    @GetMapping("/{id}")
    public Object queryItemById(@PathVariable("id") Integer id) {
        return itemService.queryItemById(id);
    }
}


```

**5. 启动类：主要存放配置文件和启动类**

pom.xml：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springcloud-microservice-provider</artifactId>
        <groupId>com.ccb.springcloud.provider</groupId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springcloud-microservice-provider-app</artifactId>

    <dependencies>
        <!-- 把实现类项目引进来 -->
        <dependency>
            <groupId>com.ccb.springcloud.provider</groupId>
            <artifactId>springcloud-microservice-provider-service-impl</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>

        <!-- springboot 整合 mybatis-->
        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
        </dependency>

        <!-- alibaba 连接池-->
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid-spring-boot-starter</artifactId>
        </dependency>

        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
        </dependency>

        <!--导入 Eureka 服务的依赖-->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
        </dependency>

    </dependencies>
    
</project>


```

这里把 service-impl 项目依赖进来就可以了，因为 service-impl 继承了 service-inf 和 common-api。

创建启动类：

```java
package com.ccb.springcloud.provider.app;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.ComponentScan;

@EnableDiscoveryClient      // 声明这是 Eureka 的客户端
@ComponentScan(basePackages = {"com.ccb.springcloud.provider"})  //扫描主包
@MapperScan(basePackages = {"com.ccb.springcloud.provider.common.mapper"})
@SpringBootApplication
public class ItemApplication {

    public static void main(String[] args) {
        SpringApplication.run(ItemApplication.class, args);
    }
}


```

配置文件 application.properties:

```
# 应用端口号
server.port=8084

# 应用名称
spring.application.name=springcloud-microservice-item

# 是否需要将自己注册到注册中心中,默认值 true
eureka.client.registerWithEureka=true

# 是否从注册中心中获取注册信息,默认值 true
eureka.client.fetchRegistry=false

# 客户端和服务端进行交互的地址
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:6868/eureka/

# 将自己的 ip 地址注册到 Eureka 服务中
eureka.instance.prefer-ip-address=true

spring.datasource.name=mysql_test
spring.datasource.type=com.alibaba.druid.pool.DruidDataSource

#druid 相关配置

#监控统计拦截的 filters
spring.datasource.druid.filters=stat
spring.datasource.druid.driver-class-name=com.mysql.jdbc.Driver
#基本属性
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
#打开 PSCache，并指定每个连接上 PSCache 的大小。oracle 设为 true，mysql 设为 false。分库分表较多推荐设置为 false
spring.datasource.druid.pool-prepared-statements=false
spring.datasource.druid.max-pool-prepared-statement-per-connection-size=20

#mybatis 配置
mybatis.mapper-locations=classpath:mapping/*.xml
mybatis.type-aliases-package=com.ccb.springcloud.provider.common.model

```

**6. 测试**
启动注册中心 EurekaService，和 ItemApplication
![](http://plsbxlixi.bkt.clouddn.com/FqN0t6eHx1Ujk4ci-FyPfHILRDyb)
使用浏览器测试：
查看 Eureka 监控，可见已经注册成功了。
![](http://plsbxlixi.bkt.clouddn.com/Fm-AbPye98exT41Mj6_UW33W3HJO)
测试商品查询：
![](http://plsbxlixi.bkt.clouddn.com/FqsBiKd7jEIKjBHq8eTWBjDkg3UX)

测试成功。但是发现响应数据变成了 xml 格式。
这是因为我们引入了 eureka server 的依赖，导致破坏了之前 SpringMVC 默认的配置，从而导致了响应成了 xml。
解决方法：启动类中排除 eureka server 中的 xml 依赖，如下：

```xml
<!--导入 Eureka 服务的依赖-->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
    <!-- 排除 xml 依赖-->
    <exclusions>
        <exclusion>
            <groupId>com.fasterxml.jackson.dataformat</groupId>
            <artifactId>jackson-dataformat-xml</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

重启 ItemService，再次测试：
![](http://plsbxlixi.bkt.clouddn.com/Fhmcs3pLLoG0XeV7xwOxZPIrNxAT)

最后来看一下整个项目的结构：
![](http://plsbxlixi.bkt.clouddn.com/FjvomzgG4UhkZ-xaE3tRGEwTnjPm)
![](http://plsbxlixi.bkt.clouddn.com/FvMCHxPxeLNLV1oxmYR6JKFomwLu)

#### 服务消费者 (springcloud-microservice-eureka)

开发步骤与服务提供者类似，不同的是，这里订单服务除了查询订单基本信息外，还需要通过 order_details 把关联的商品 id 查询出来，然后通过服务发现与注册机制，从注册中心获取服务提供者的 ip 和端口号，然后发送请求到服务提供者获取商品信息列表。
1.父 pom.xml，和服务提供者差不多：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ccb.springcloud.comsumer</groupId>
    <artifactId>springcloud-microservice-comsumer</artifactId>
    <packaging>pom</packaging>
    <version>1.0.0-SNAPSHOT</version>

    <modules>
        <module>springcloud-microservice-comsumer-app</module>
        <module>springcloud-microservice-comsumer-common-api</module>
        <module>springcloud-microservice-comsumer-service-inf</module>
        <module>springcloud-microservice-comsumer-service-impl</module>
    </modules>

    <name>springcloud-microservice-comsumer</name>
    <description>Demo project for Spring Cloud</description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.0.7.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>

    <properties>
        <java.version>1.8</java.version>
        <!--springboot 2.0.x 使用 Finchley.SR2 版本-->
        <spring-cloud.version>Finchley.SR2</spring-cloud.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <!--<导入 spring cloud 依赖管理 >-->
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <dependency>
                <groupId>org.mybatis.spring.boot</groupId>
                <artifactId>mybatis-spring-boot-starter</artifactId>
                <version>1.3.2</version>
            </dependency>

            <!-- 导入 alibaba 连接池-->
            <dependency>
                <groupId>com.alibaba</groupId>
                <artifactId>druid-spring-boot-starter</artifactId>
                <version>1.1.9</version>
            </dependency>

            <dependency>
                <groupId>mysql</groupId>
                <artifactId>mysql-connector-java</artifactId>
                <version>5.1.47</version>
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

2.common-api：使用插件自动创建 items 表实体类和 mapper 类
参考上文，方法类似，在 resource 下创建 generator/generatorConfig.xml，这里生成两个表 orders 和 order_details，内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE generatorConfiguration PUBLIC
      "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"
      "http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd">
<generatorConfiguration>
   <!-- 数据库驱动包位置 -->
   <classPathEntry
         location="D:\Maven\.m2\repository\mysql\mysql-connector-java\5.1.47\mysql-connector-java-5.1.47.jar" />
   <!-- <classPathEntry location="C:\oracle\product\10.2.0\db_1\jdbc\lib\ojdbc14.jar" 
      /> -->
   <context id="MySqlTables" targetRuntime="MyBatis3">
      <commentGenerator>
         <property name="suppressAllComments" value="true" />
      </commentGenerator>
      <!-- 数据库链接 URL、用户名、密码 -->
      <jdbcConnection driverClass="com.mysql.jdbc.Driver"
                  connectionURL="jdbc:mysql://localhost:3306/mydatabase" userId="root"
                  password="root">
         <!--<jdbcConnection driverClass="oracle.jdbc.driver.OracleDriver" connectionURL="jdbc:oracle:thin:@localhost:1521:orcl" 
            userId="msa" password="msa"> -->
      </jdbcConnection>
      <javaTypeResolver>
         <property name="forceBigDecimals" value="false" />
      </javaTypeResolver>
      <!-- 生成实体类的包名和位置，这里配置将生成的实体类放在 com.ccb.springcloud.comsumer.common.model 这个包下 -->
      <javaModelGenerator targetPackage="com.ccb.springcloud.comsumer.common.model"
                     targetProject="src/main/java">
         <property name="enableSubPackages" value="true" />
         <property name="trimStrings" value="true" />
      </javaModelGenerator>
      <!-- 生成的 SQL 映射文件包名和位置，这里配置将生成的 SQL 映射文件放在 src/main/resources 的 mapping 下 -->
      <sqlMapGenerator targetPackage="mapping"
                   targetProject="src/main/resources">
         <property name="enableSubPackages" value="true" />
      </sqlMapGenerator>
      <!-- 生成 DAO 的包名和位置，这里配置将生成的 dao 类放在 com.ccb.springcloud.comsumer.common.mapper 这个包下 -->
      <javaClientGenerator type="XMLMAPPER"
                      targetPackage="com.ccb.springcloud.comsumer.common.mapper" targetProject="src/main/java">
         <property name="enableSubPackages" value="true" />
      </javaClientGenerator>
      <!-- 要生成那些表 (更改 tableName 和 domainObjectName 就可以) -->
      <table tableName="orders" domainObjectName="Order"
            enableCountByExample="false" enableUpdateByExample="false"
            enableDeleteByExample="false" enableSelectByExample="false"
            selectByExampleQueryId="false" />
      <table tableName="order_details" domainObjectName="OrderDetail"
            enableCountByExample="false" enableUpdateByExample="false"
            enableDeleteByExample="false" enableSelectByExample="false"
            selectByExampleQueryId="false" />
   </context>
</generatorConfiguration>

```

创建 maven 插件启动命令，生成 model，mapper dao，mapper xml 代码，参考上一节。
由于需要在 order_details 中通过 order_id 查询对应的 item_id，所以在 OrderDetailMapper 中添加一个方法：

```java
List<OrderDetail> selectByOrderId(Integer orderId);   //新增，根据 orderId 查询数据
```

对应的 xml：

```xml
<select id="selectByOrderId" resultMap="BaseResultMap" parameterType="java.lang.Integer" >
  select
  <include refid="Base_Column_List" />
  from order_details
  where order_id = #{orderId,jdbcType=INTEGER}
</select>
```

3.service-inf：把 common-api 依赖进来，还需要用到服务提供者的接口

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springcloud-microservice-comsumer</artifactId>
        <groupId>com.ccb.springcloud.comsumer</groupId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springcloud-microservice-comsumer-service-inf</artifactId>

    <dependencies>
        <!-- 引入 commsumer common-api-->
        <dependency>
            <groupId>com.ccb.springcloud.comsumer</groupId>
            <artifactId>springcloud-microservice-comsumer-common-api</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>

        <!-- 引入 provider service-inf-->
        <dependency>
            <groupId>com.ccb.springcloud.provider</groupId>
            <artifactId>springcloud-microservice-provider-service-inf</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>
    </dependencies>

</project>


```

创建一个返回对象实体类：

```java
package com.ccb.springcloud.comsumer.io;

import com.ccb.springcloud.provider.common.model.Item;

import java.io.Serializable;
import java.util.Date;
import java.util.List;

/**
 * 返回对象实体类
 */
public class OrderInfo implements Serializable {

    private static final long serialVersionUID = 1L;

    private Integer orderId;

    private Integer userId;

    private String userName;

    private Date createTime;

    private Date updateTime;

    private List<Item> items;	//商品列表

//省略 getter 和 setter

}

```

创建订单服务查询接口：

```java
package com.ccb.springcloud.comsumer.service;

import com.ccb.springcloud.comsumer.io.OrderInfo;

public interface OrderService {

    // 查询单笔订单数据
    OrderInfo queryOrderById(Integer id);
}

```

4.service-impl

pom.xml：把 service-inf 依赖进来

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springcloud-microservice-comsumer</artifactId>
        <groupId>com.ccb.springcloud.comsumer</groupId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springcloud-microservice-comsumer-service-impl</artifactId>

    <dependencies>
        <!-- 导入 service 接口-->
        <dependency>
            <groupId>com.ccb.springcloud.comsumer</groupId>
            <artifactId>springcloud-microservice-comsumer-service-inf</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- 导入 Eureka 服务的依赖 -->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
            <exclusions>
                <exclusion>
                    <groupId>com.fasterxml.jackson.dataformat</groupId>
                    <artifactId>jackson-dataformat-xml</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
    </dependencies>

</project>

```

创建一个远程调用商品服务的类 ItemServiceRemote：这里查询很关键，商品列表需要依赖 Eureka 客户端服务发现获取服务提供者 ip 地址和端口号，然后构造 http 请求查询商品信息。

```java
/**
 * 远程查询商品列表服务
 */

@Service
public class ItemServiceRemote {

    @Autowired
    private DiscoveryClient discoveryClient;

    @Autowired
    private RestTemplate restTemplate;

    // 查询商品列表
    Item queryItemById(Integer itemId) {
        // 使用 HttpClient 工具发送请求获取商品的数据
        // 我们也可以使用 spring 给我们提供的另个一个类 RestTemplate,来发送 Http 请求
        String itemServiceId = "springcloud-microservice-item";

        //服务发现，返回实例
        List<ServiceInstance> instances =
                discoveryClient.getInstances(itemServiceId);

        if (instances == null || instances.isEmpty()) {
            return null;
        }

        ServiceInstance instance = instances.get(0);
//获取主机 ip 和端口号
        String url = "http://" + instance.getHost()
                + ":" +instance.getPort() + "/item/";
        System.out.println("url = [" + url + itemId + "]");
        Item item = restTemplate.getForObject(url + itemId, Item.class);

        // 返回
        return item;
    }

}

```

OrderServiceImpl：分别把 订单 和 商品列表 查询出来

```java
package com.ccb.springcloud.comsumer.service.impl;
// 省略 import

@Service
public class OrderServiceImpl implements OrderService {

    @Autowired
    private OrderMapper orderMapper;

    @Autowired
    private OrderDetailMapper orderDetailMapper;

@Autowired
private ItemServiceRemote itemServiceRemote;    //将查询商品服务注进来


    @Override
    public OrderInfo queryOrderById(Integer id) {
        OrderInfo orderInfo = new OrderInfo();

        //查询订单数据
        Order order = orderMapper.selectByPrimaryKey(id);

        //商品列表
        List<Item> itemList = new ArrayList<>();

        List<OrderDetail> orderDetails = orderDetailMapper.selectByOrderId(id);

        for (OrderDetail orderDetail:orderDetails) {
            Item item = itemServiceRemote.queryItemById(orderDetail.getItemId());
            itemList.add(item);
        }

        orderInfo.setOrderId(order.getId());
        orderInfo.setUserId(order.getUserId());
        orderInfo.setUserName(order.getUserName());
        orderInfo.setCreateTime(order.getCreateTime());
        orderInfo.setUpdateTime(order.getUpdateTime());
        orderInfo.setItems(itemList);

        return orderInfo;
    }

}

```

5.启动类 app
pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>springcloud-microservice-comsumer</artifactId>
        <groupId>com.ccb.springcloud.comsumer</groupId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>springcloud-microservice-comsumer-app</artifactId>

    <dependencies>
        <dependency>
            <groupId>com.ccb.springcloud.comsumer</groupId>
            <artifactId>springcloud-microservice-comsumer-service-impl</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>

        <!-- springboot 整合 mybatis-->
        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
        </dependency>

        <!-- alibaba 连接池-->
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid-spring-boot-starter</artifactId>
        </dependency>

        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
        </dependency>

        <!--导入 Eureka 服务的依赖-->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
            <!-- 排除 xml 依赖-->
            <exclusions>
                <exclusion>
                    <groupId>com.fasterxml.jackson.dataformat</groupId>
                    <artifactId>jackson-dataformat-xml</artifactId>
                </exclusion>
            </exclusions>
        </dependency>

        <!-- 添加 OkHttp 依赖 -->
        <dependency>
            <groupId>com.squareup.okhttp3</groupId>
            <artifactId>okhttp</artifactId>
        </dependency>
    </dependencies>

</project>

```

创建启动类 OrderApplication：

```java
package com.ccb.springcloud.comsumer.app;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.http.client.OkHttp3ClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

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

配置文件 application.properties：

```
# 应用端口号
server.port=8085

# 应用名称
spring.application.name=springcloud-microservice-order

# 是否需要将自己注册到注册中心中,默认值 true
eureka.client.registerWithEureka=true

# 是否从注册中心中获取注册信息,默认值 true。(这里和服务提供者不同)
eureka.client.fetchRegistry=true

# 客户端和服务端进行交互的地址
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:6868/eureka/

# 将自己的 ip 地址注册到 Eureka 服务中
eureka.instance.prefer-ip-address=true


spring.datasource.name=mysql_test
spring.datasource.type=com.alibaba.druid.pool.DruidDataSource

#druid 相关配置

#监控统计拦截的 filters
spring.datasource.druid.filters=stat
spring.datasource.druid.driver-class-name=com.mysql.jdbc.Driver
#基本属性
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
#打开 PSCache，并指定每个连接上 PSCache 的大小。oracle 设为 true，mysql 设为 false。分库分表较多推荐设置为 false
spring.datasource.druid.pool-prepared-statements=false
spring.datasource.druid.max-pool-prepared-statement-per-connection-size=20

#mybatis配置
mybatis.mapper-locations=classpath:mapping/*.xml
mybatis.type-aliases-package=com.ccb.springcloud.comsumer.common.model

```

6.启动测试
![](http://plsbxlixi.bkt.clouddn.com/FpDcmCIhgqVf_v-vQJ8x94_upDCo)
Eureka 注册成功
![](http://plsbxlixi.bkt.clouddn.com/FvL1Nj5jibYETyVHPg1Rts9fdTCA)
浏览器测试，可见对应的商品信息也查出来了
![](http://plsbxlixi.bkt.clouddn.com/FkLYJXKHDXn_638gy9Vu2yUupxNY)

最后来看一下项目结构，和服务提供者差不多：
![](http://plsbxlixi.bkt.clouddn.com/FmWEnL0p0-qRWUTnYuUV5q1-r45v)
![](http://plsbxlixi.bkt.clouddn.com/FiJ3EBSgwoHXvtLeIHWRKDfdnLQg)

#### Eureka集群
前面的测试发现，Eureka是一个单点服务，在生产环境容易发生单点故障，为了确保服务的高可用，我们需要搭建 Eureka集群。

思路：Eureka 本身作为一个服务，提供注册的功能，如果启动多个 Eureka服务，彼此之间互相注册，就形成了一个集群。
* 修改springcloud-microservice-eureka 配置文件，启动服务：

```
# 服务端口号(搭建集群时，换不同的端口号启动服务)
server.port=6868

# 应用名称
spring.application.name=springcloud-microserice-eureka(6868)
# 是否需要将自己注册到注册中心中,因为本身就是一个注册中心,所以不需要将自己注册到注册中心中
# 搭建集群时，改为true
eureka.client.registerWithEureka=true

# 是否从注册中心中获取注册信息(搭建集群时改为true)
eureka.client.fetchRegistry=true

# 客户端和服务端进行交互的地址
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:6869/eureka/
```

* 修改配置文件的端口号，再启动一个服务(需要点击工具栏 – Edit Configurations… - 勾上“Allow running in parallel”)：

```
# 服务端口号(搭建集群时，换不同的端口号启动服务)
server.port=6869

# 应用名称
spring.application.name=springcloud-microserice-eureka(6869)
# 是否需要将自己注册到注册中心中,因为本身就是一个注册中心,所以不需要将自己注册到注册中心中
# 搭建集群时，改为true
eureka.client.registerWithEureka=true

# 是否从注册中心中获取注册信息(搭建集群时改为true)
eureka.client.fetchRegistry=true

# 客户端和服务端进行交互的地址
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:6868/eureka/
```
* 查看结果:
  ![](http://plsbxlixi.bkt.clouddn.com/Fmbygx3TqhE8aM0b-JC-Tr06y7jS)
  ![](http://plsbxlixi.bkt.clouddn.com/FpQ9qzMPr-8t0z80KacIVJ35PSyP)

#### 将服务注册到 Eureka 集群
修改配置文件，只需要添加集群的地址，用逗号隔开:

```
# 客户端和服务端进行交互的地址
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:6868/eureka/,http://127.0.0.1:6869/eureka/
```
访问 http://localhost:6868/ 和  http://localhost:6869/ 
![](http://plsbxlixi.bkt.clouddn.com/FmoqUvKR_8QgxIvP465gPyfQcEe4)
发现在Eureka的两个Server中都注册对应的商品和订单服务。

可以尝试关闭一个 Eureka 服务，看订单服务是否能调用成功。



**推荐阅读：**

[Spring Cloud 及 Eureka 注册中心](https://turbobin.github.io/2019/01/07/springcloud-and-eureka/)



> 本文首发于 [turbobin's Blog](https://turbobin.github.io/) 。转载请注明出处，附上本原文链接， 谢谢合作。

