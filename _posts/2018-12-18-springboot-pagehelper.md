---
layout:     post
title:      Spring Boot 实现分页查询 – pagehelper
subtitle:   
date:       2018-12-18
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
tags:
    - [微服务, spring boot]
---
接上一节 [Spring Boot 整合 Mybatis，与数据库交互]({{site.url}}/2018/12/17/springboot-with-mybatis/) 上面有个方法是查询所有用户列表，这里要考虑一个问题了：如果数据库表数据量特别大，然后发送一个查询所有列表的请求，响应超时是肯定的了，后台一下子返回这么大的数据，有可能导致整个服务挂起。解决这个问题的方法就是禁止查询所有列表，实现分页查询，设置默认分页参数。

>Java version：1.8+  
Maven：3.3+，我这里使用的 3.5.3  
SpringBoot：2.0.7.RELEASE  
IDE开发工具：IDEA 专业版。

**Step1:添加分页插件依赖包：**

```xml
<!-- 分页插件 -->
<dependency>
    <groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper-spring-boot-starter</artifactId>
    <version>1.2.5</version>
</dependency>
```

**Step2：在application.properties中添加参数：**

```
# pagehelper配置
pagehelper.helper-dialect=mysql
pagehelper.reasonable=true
pagehelper.support-methods-arguments=true
pagehelper.params="count=countSql"
pagehelper.returnPageInfo=check

```

**Step3：在UserService接口中添加方法：**

```java

//添加分页查询方法
PageInfo<User> findAllUsers(int page, int pagesize);

```
实现类UserServiceImpl：
```java
    @Override
    public PageInfo<User> findAllUsers(int page, int pagesize) {
        //将参数传给这个方法就可以实现物理分页了，非常简单。
        PageHelper.startPage(page, pagesize);
        List<User> users = userMapper.selectAllUsers();
//        PageInfo<User> all = new PageInfo<>(users);
        return new PageInfo<>(users);
    }

```

**Step4：UserController**

```java

//分页查询
@GetMapping("/pagehelper")
public Object findAllUsers(
        @RequestParam(name = "page", required = false, defaultValue = "1")
                int page,
        @RequestParam(name = "pagesize", required = false, defaultValue = "2")
        int pagesize) {
    return userService.findAllUsers(page, pagesize);
}

```
默认参数是从第1页开始，一页返回2条数据，可以根据情况修改上述参数。

**Step5：测试（推荐一个Chrome插件：`基于REST的web服务客户端`，POSTman软件的插件版）**

![]({{site.url}}/img/java/springboot-18.png)
![]({{site.url}}/img/java/springboot-19.png)
![]({{site.url}}/img/java/springboot-20.png)

可以使用默认参数，也可以使用 “page”、“pagesize” 参数的自由组合进行查询。


>写技术博客不易，转载请注明出处，附上原文链接。谢谢合作。