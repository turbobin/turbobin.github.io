---
layout:     post
title:      Spring Boot 使用 JPA 简化数据库的访问
subtitle:   
date:       2018-12-19
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
tags:
    - [微服务, spring boot]
---
JPA全称是Java Persistence API，是一个基于ORM映射的标准规范，采用“约定优先于配置”的原则，按照特定的规则，在接口层就实现了对象关系映射，省去了很多配置。目前，JPA大多依赖Hibernate来实现。

>Java version：1.8+  
Maven：3.3+，我这里使用的 3.5.3  
SpringBoot：2.0.7.RELEASE  
IDE开发工具：IDEA 专业版。


创建一个maven项目，引入JPA依赖
```xml
<!--添加JPA依赖包-->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

```
或者在IDEA中利用脚手架构建Spring Boot项目时勾选JPA
![]({{site.url}}/img/java/springboot-21.png)

完整 POM.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ccb.springboot</groupId>
    <artifactId>springboot-jpa-01</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <!-- Inherit defaults from Spring Boot -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.0.7.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!--添加JPA依赖包-->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!--mysql驱动-->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>5.1.47</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>

```
配置文件application.properties：

```properties
spring.datasource.url=jdbc:mysql://127.0.0.1:3306/mydatabase?useSSL=false&useUnicode=true&characterEncoding=UTF-8&allowMultiQueries=true
spring.datasource.username=root
spring.datasource.password=root
spring.datasource.driver-class-name=com.mysql.jdbc.Driver

# JPA配置
spring.jpa.hibernate.ddl-auto=update
# 是否在控制台打印sql语句
spring.jpa.show-sql=true
# Spring boot 2.0 居然默认的是MyISAM引擎，这里需要指定为InnoDB
spring.jpa.database-platform=org.hibernate.dialect.MySQL5InnoDBDialect

```
spring.jpa.hibernate.ddl-auto 是 hibernate 的配置属性，其主要作用是：自动创建、更新、验证数据库表结构。该参数的几种配置如下：
* `create`：每次加载hibernate时都会删除上一次的生成的表，然后根据你的model类再重新来生成新表，哪怕两次没有任何改变也要这样执行，这就是导致数据库表数据丢失的一个重要原因。
* `create-drop`：每次加载hibernate时根据model类生成表，但是sessionFactory一关闭,表就自动删除。
* `update`：最常用的属性，第一次加载hibernate时根据model类会自动建立起表的结构（前提是先建立好数据库），以后加载hibernate时根据model类自动更新表结构，即使表结构改变了但表中的行仍然存在不会删除以前的行。要注意的是当部署到服务器后，表结构是不会被马上建立起来的，是要等应用第一次运行起来后才会。
* `validate`：每次加载hibernate时，验证创建数据库表结构，只会和数据库中的表进行比较，不会创建新表，但是会插入新值。

下面还是按分层结构来创建实体类，DAO，Service 和 Controller

实体类 User：
```java
package com.ccb.springboot.domain;

import javax.persistence.*;

@Entity     //标注为数据库对应实体类
@Table(name = "users")  //当表名和实体名称不一致时，必须声明
public class User {

    @Id
    @GeneratedValue     //标注主键自增
    private Integer id;

    @Column(length = 40)    //声明实体类属性，length只对String类型有效
    private String username;

    @Column(length = 50)
    private String password;

    @Column(length = 40)
    private String email;

    @Column(length = 10)
    private String sex;

    @Column
    private Integer age;

    @Column(length = 30)
    private String city;

//省略getter和setter和构造函数

}

```

UserRepository（DAO）:

```java

/**
 * 数据访问接口
 */
public interface UserRepository extends JpaRepository<User, Long> {

//    List<User> findALL();     //继承JpaRepository，已实现findALL方法

    User findUserById(Integer id);

    User findUserByUsername(String name);

    @Query("from User u where u.age=:age")  //注意这里User表示实体类名
    List<User> findUser(@Param("age") Integer age);


}

```
JpaRepository接口本身已经实现了创建（save）、更新（save）、删除（delete）、查询（findAll、findOne）等基本操作的函数，因此对于这些基础操作的数据访问就不需要开发者再自己定义。

Jpa可以根据解析方法名如 findUserById(Integer id)、findByNameAndAge(String name, Integer age) 去自动创建查询。

UserService：

```java

public interface UserService {

    List<User> findAllUsers();

    User findUserById(Integer id);

    User findUserByName(String name);
}

```

UserServiceImpl：

```java

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userDao;

    @Override
    public List<User> findAllUsers() {
        return userDao.findAll();
    }

    @Override
    public User findUserById(Integer id) {
        return userDao.findUserById(id);
    }

    @Override
    public User findUserByName(String name) {
        return userDao.findUserByUsername(name);
    }
}

```

UserController：

```java

/**
 * 控制层：调用业务层查询数据
 */
@RestController
@RequestMapping(value = "user")
public class UserController {

    @Autowired
    private UserService userService;

    //这里也可以直接把UserRepository注进来，直接调用接口方法
    @Autowired
    private UserRepository userRepository;

    //查询所有用户列表
    @RequestMapping(value = "/all")
    public List<User> selectAllUsers(){
        return userService.findAllUsers();
//        return userRepository.findAll();

    }

    //根据id查询用户
    @RequestMapping(value = "/id/{id}")
    public User selectUserById(@PathVariable("id") Integer userId) {
        return userService.findUserById(userId);
    }

    //根据用户名查询用户
    @RequestMapping(value = "/name/{name}")
    public User selectUserByName(@PathVariable("name") String username) {
        return userService.findUserByName(username);
    }

    //根据年龄查询数据
    @RequestMapping(value = "/age/{age}")
    public Object findUserByAge(@PathVariable("age") Integer age) {
        return userRepository.findUser(age);
    }

}

```

开启启动类，用浏览器测试：

![]({{site.url}}/img/java/springboot-22.png)
![]({{site.url}}/img/java/springboot-23.png)
![]({{site.url}}/img/java/springboot-24.png)
![]({{site.url}}/img/java/springboot-25.png)

最后的项目结构：

![]({{site.url}}/img/java/springboot-26.png)

**小结：**

可以看出，使用Jpa在接口层就实现了数据对象关系映射，可以大大简化配置，也可以使用注解方式写入sql语句，比较灵活。一个缺点是，当项目越来越大，查询比较复杂时，可能需要在java类中写入大量sql，不是一个好办法，而mybatis一个好处是可以实现sql和java代码分离。

**推荐阅读：**

[基于Spring Boot整合Mybatis，与数据库交互]({{site.url}}/2018/12/17/springboot-with-mybatis/)

[Spring Boot 实现分页查询 – pagehelper]({{site.url}}/2018/12/18/springboot-pagehelper/)

>写技术博客不易，转载请注明出处，附上原文链接[https://turbobin.github.io/](https://turbobin.github.io/) , 谢谢合作。