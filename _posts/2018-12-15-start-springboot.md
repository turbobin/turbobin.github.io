---
layout:     post
title:      微服务架构-从 Spring Boot 开始
subtitle:   使用 maven 构建 Spring Boot 应用
date:       2018-12-15
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
tags:
    - 微服务，spring boot
---

### 简述
Spring Boot是用来简化Spring的应用从搭建到开发的过程，集成了Spring开发中的各种依赖包，包括IOC、AOP依赖包，日志管理包，测试包，达到了真正的开箱即用。并且，spring boot极大简化了Spring的配置，提升了开发效率。

### 使用 maven 构建 Spring Boot 应用
>Java version：1.8+  
Maven：3.3+，我这里使用的 3.5.3  
SpringBoot：2.0.7.RELEASE  
IDE 开发工具：IDEA专业版。	SpringBoot 项目这里强烈推荐 IDEA，功能强大且智能。当然坚持用 eclipse/myclipse 也可以，推荐安装一个 sts 插件会好一点。

#### 1. 创建一个新的 maven 项目，从官网添加 pom 父依赖

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
   <modelVersion>4.0.0</modelVersion>

   <groupId>com.example</groupId>
   <artifactId>demo</artifactId>
   <version>0.0.1-SNAPSHOT</version>
   <packaging>jar</packaging>

   <name>demo</name>
   <description>Demo project for Spring Boot</description>
   <!-- Inherit defaults from Spring Boot -->
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
   </properties>

   <dependencies>
      <dependency>
         <groupId>org.springframework.boot</groupId>
         <artifactId>spring-boot-starter</artifactId>
      </dependency>

      <dependency>
         <groupId>org.springframework.boot</groupId>
         <artifactId>spring-boot-starter-test</artifactId>
         <scope>test</scope>
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
可以看到，只需要继承`spring-boot-starter-parent`，Spring 的开发包都引进来了
![]({{site.url}}/img/java/springboot-01.png)

在`src/main/java`目录下新建一个`com.example.demo`包，在此包下新建一个`DemoApplication.java`

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication    //引入SpringBoot注解
public class DemoApplication {

   public static void main(String[] args) {
	//Spring Boot启动方法
      SpringApplication.run(DemoApplication.class, args);   }
}

```
启动类默认会扫描所有`com.example.demo`包及其子包下的项目文件。

#### 2.	利用 IDEA Spring Initializr 自动构建 Spring Boot 项目
其原理是调用官网的脚手架接口快速构建，不过用IDEA从构建到导入项目一步到位，更方便快捷。  
官网快速构建：打开[https://start.spring.io/](https://start.spring.io/)
![]({{site.url}}/img/java/springboot-02.png)

IDEA 构建:
![]({{site.url}}/img/java/springboot-03.png)

填写 maven 项目中的 groupId 和 artifaId，以及其他 version、package信息
![]({{site.url}}/img/java/springboot-04.png)

选择 Spring Boot 版本，左边是可选的依赖（也包含了很多 Spring Cloud 依赖）
![]({{site.url}}/img/java/springboot-05.png)

一路 Next，就生成了基本的 Spring Boot 应用。
