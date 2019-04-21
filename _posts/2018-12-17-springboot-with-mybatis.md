---
layout:     post
title:      Spring Boot 整合 Mybatis，与数据库交互
subtitle:   
date:       2018-12-17
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
category: 技术
tags:
    - [微服务, spring boot]
---
上一节 [基于 Spring Boot 来开发 Spring 项目]({{site.url}}/2018/12/16/spring-with-springboot/) Controller 调用 Service 查询使用的是静态数据，下面来用 Spring Boot 整合 Mybatis 与数据库进行交互。

>Java version：1.8+  
Maven：3.3+，我这里使用的 3.5.3  
SpringBoot：2.0.7.RELEASE  
IDE开发工具：IDEA 专业版。

新建一个 maven 项目：`springboot-mybatis-01`，  
主包名：`com.ccb.sprngboot`，启动类：`SpringbootMybatisApplication.java` 

添加几个依赖包：
```
mybatis：mybatis-spring-boot-starter
mysql：mysql-connector-java
数据库连接池用的是阿里巴巴的druid：druid-spring-boot-starter
```

完整 POM：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.0.7.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.ccb.springboot</groupId>
    <artifactId>springboot-mybatis-01</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>jar</packaging>
    <name>springboot-mybatis-01</name>
    <description>use mybatis with Spring Boot</description>

    <properties>
        <java.version>1.8</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
            <version>1.3.2</version>
        </dependency>

        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>

        <!-- alibaba的druid数据库连接池 -->
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid-spring-boot-starter</artifactId>
            <version>1.1.9</version>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>

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
上面提供了一个 mybatis 自动生成代码插件，一会儿来体验一下。

先创建数据库表：
```sql
CREATE DATABASE mydatabase DEFAULT CHARSET utf8;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(40) DEFAULT NULL,
  `password` varchar(50) DEFAULT NULL,
  `email` varchar(40) DEFAULT NULL,
  `sex` varchar(10) DEFAULT NULL,
  `age` int(3) DEFAULT NULL,
  `city` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

```

插入一些数据：
![]({{site.url}}/images/java/springboot-09.png)

下面有两种方法来生成mybatis代码：

**1. IDEA + mybatis maven 插件**

在src/main/resources下创建generator/generatorConfig.xml，内容如下：
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
      <!-- 数据库链接URL、用户名、密码 -->
      <jdbcConnection driverClass="com.mysql.jdbc.Driver"
                  connectionURL="jdbc:mysql://localhost:3306/mydatabase" userId="root" password="root">
         <!--<jdbcConnection driverClass="oracle.jdbc.driver.OracleDriver" connectionURL="jdbc:oracle:thin:@localhost:1521:orcl" 
            userId="msa" password="msa"> -->
      </jdbcConnection>
      <javaTypeResolver>
         <property name="forceBigDecimals" value="false" />
      </javaTypeResolver>
      <!-- 生成实体类的包名和位置，这里配置将生成的实体类放在com.ccb.springboot.entity这个包下 -->
      <javaModelGenerator targetPackage="com.ccb.springboot.entity"
                     targetProject="src/main/java">
         <property name="enableSubPackages" value="true" />
         <property name="trimStrings" value="true" />
      </javaModelGenerator>
      <!-- 生成的SQL映射文件包名和位置，这里配置将生成的SQL映射文件放在src/main/resources的mapping下 -->
      <sqlMapGenerator targetPackage="mapping"
                   targetProject="src/main/resources">
         <property name="enableSubPackages" value="true" />
      </sqlMapGenerator>
      <!-- 生成DAO的包名和位置，这里配置将生成的dao类放在com.ccb.springboot.mapper这个包下 -->
      <javaClientGenerator type="XMLMAPPER"
                      targetPackage="com.ccb.springboot.mapper" targetProject="src/main/java">
         <property name="enableSubPackages" value="true" />
      </javaClientGenerator>
      <!-- 要生成那些表(更改tableName和domainObjectName就可以) -->
      <table tableName="users" domainObjectName="User"
            enableCountByExample="false" enableUpdateByExample="false"
            enableDeleteByExample="false" enableSelectByExample="false"
            selectByExampleQueryId="false" />
   </context>
</generatorConfiguration>

```
点击工具栏上的 Run——EditConfigrations,选择 maven（如果没有就点 +，选择 maven）
![]({{site.url}}/images/java/springboot-10.png)
![]({{site.url}}/images/java/springboot-11.png)

选择名称，点击运行
![]({{site.url}}/images/java/springboot-12.png)
这样就自动生成了实体类User，UserMapper（DAO）和 UserMapper.xml

**2. 命令行 + mybatis-generator-core jar包**

下载`mybatis-generator-core-1.3.5.jar`包，和 generatorConfig.xml 一起放在 src 同级目录下，在命令行敲如命令：  
`java –jar mybatis-generator-core-1.3.5.jar –configfile generatorConfig.xml -overwrite`
![]({{site.url}}/images/java/springboot-13.png)
![]({{site.url}}/images/java/springboot-14.png)

接下来创建 Service 和 Controller：

UserService:

```java

/**
 * 业务层接口
 */

public interface UserService {

    // 增
    int addUser(User user);

    // 删
    int deleteUserById(Integer userId);

    // 改
    int updateUser(User user);

    // 查
    User selectUserById(Integer userId);

    List<User> selectAllUsers();    //新增，查询列表，UserMapper中记得添加这个方法
}

```

UserServiceImpl：

```java
@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserMapper userMapper;

    @Override
    public int addUser(User user) {
        return userMapper.insert(user);
    }

    @Override
    public int deleteUserById(Integer userId) {
        return userMapper.deleteByPrimaryKey(userId);
    }

    @Override
    public int updateUser(User user) {
        return userMapper.updateByPrimaryKeySelective(user);
    }

    @Override
    public User selectUserById(Integer userId) {
        return userMapper.selectByPrimaryKey(userId);
    }

    @Override
    public List<User> selectAllUsers() {
        return userMapper.selectAllUsers();
    }

}

```
UserController：

```java

/**
 * 控制层
 */
@RestController
@RequestMapping(value = "user")
public class UserController {

    @Autowired
    private UserService userService;

    //查询所有用户列表
    @RequestMapping(value = "/all")
    public List<User> selectAllUsers(){
        return userService.selectAllUsers();

    }

    //根据id查询用户
    @RequestMapping(value = "/{id}")
    public User selectUserById(@PathVariable("id") Integer userId) {
        return userService.selectUserById(userId);
    }

}

```
这里只实现了两个查询方法，其他增删改类似。

打开UserMapper.java，做点小改动：

```java

@Repository //注册DAO到spring容器中
@Mapper     // mybatis注解，标注mapper，需要mybatis版本3.3+，如果不写这个注解，需要在启动类中使用@ComponentScan(basePackages ="com.ccb.springboot.mapper")配置扫描包
public interface UserMapper {
    int deleteByPrimaryKey(Integer id);

    int insert(User user);

    int insertSelective(User user);

    User selectByPrimaryKey(Integer id);

    List<User> selectAllUsers();    // 新增查询列表方法，需要对应在UserMapper.xml中添加

    int updateByPrimaryKeySelective(User user);

    int updateByPrimaryKey(User user);
}

```

最后来配置数据库连接：

打开application.properties:
```properties
server.port=8080

spring.datasource.name=mysql_test
spring.datasource.type=com.alibaba.druid.pool.DruidDataSource

#druid相关配置

#监控统计拦截的filters
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
#打开PSCache，并指定每个连接上PSCache的大小。oracle设为true，mysql设为false。分库分表较多推荐设置为false
spring.datasource.druid.pool-prepared-statements=false
spring.datasource.druid.max-pool-prepared-statement-per-connection-size=20

#mybatis配置
mybatis.mapper-locations=classpath:mapping/*.xml
mybatis.type-aliases-package=com.ccb.springboot.entity

```

启动SpringbootMybatisApplication.java，打开浏览器测试：
![]({{site.url}}/images/java/springboot-15.png)
![]({{site.url}}/images/java/springboot-16.png)

最后，看一下整个项目的结构：
![]({{site.url}}/images/java/springboot-17.png)

到这里就实现了 Spring Boot 和 mybatis 的整合，实现了与数据库的交互，不需要 mybatis 的 xml 文件，只需要很少的配置就可以完成。



**推荐阅读：**

[Spring Boot 实现分页查询 – pagehelper]({{site.url}}/2018/12/18/springboot-pagehelper/)

[Spring Boot 使用 JPA 简化数据库的访问]({{site.url}}/2018/12/19/springboot-with-jpa/)




>本文首发于 [turbobin's Blog](https://turbobin.github.io/) 。转载请注明出处，附上本原文链接， 谢谢合作。