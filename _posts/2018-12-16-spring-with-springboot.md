---
layout:     post
title:      基于 Spring Boot 来开发 Spring 项目
subtitle:   
date:       2018-12-16
author:     turbobin
header-img: img/post-bg-debug.jpg
catalog: true
tags:
    - [微服务, spring boot]
---
[上一节]({{site.url}}/2018/12/15/start-springboot/)已经构建一个Spring Boot基本应用，其实就是引入了依赖包，创建了一个启动类。
下面运用 Spring 的分层逻辑来开发一个简单的Spring项目。

**项目结构：**
![]({{site.url}}/img/java/springboot-06.png)

**User 实体类：**

```java
/**
 * 实体类
 */
public class User {

    private Integer id;

    private String name;

    private Integer age;

    private String city;
    
    //省略getter、setter和构造方法

```

**业务层接口 UserService：**

```java
import com.example.demo.domain.User;

/**
 * 业务层接口
 */
public interface UserService {

    public User findUserById(Integer id);
}


```

**业务层接口实现类：**

```java

@Service       //Spring注解，用于注册业务层
public class UserServiceImpl implements UserService {

    private static final Map<Integer, User> MAP = new HashMap<Integer, User>();

    //准备一些静态数据
    static {

        MAP.put(1, new User(1, "张三", 26, "上海"));
        MAP.put(2, new User(2, "李四", 23, "北京"));
        MAP.put(3, new User(3, "王五", 25, "深圳"));
    }

    @Override
    public User findUserById(Integer id) {
        return MAP.get(id);
    }
}

```

**Controller 层：** 

这里用到了 Spring web注解，需要先引入包：

```xml
<dependency>
   <groupId>org.springframework.boot</groupId>
   <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

```java

/**
 * 控制层调用业务层
 */
@RestController     //Spring MVC注解，返回json数据
public class UserController {

    //注入业务层
    @Autowired
    private UserService userService;

//    @RequestMapping(value = "user/{id}", method = RequestMethod.GET)
    @GetMapping("user/{id}")    // 如果是get方法，可直接使用@GetMapping注解
    public User findUserById(@PathVariable("id") Integer id) {
	//@PathVariable(“id”)表示把url中数据传入方法参数中
        return userService.findUserById(id);
    }
}

```

配置文件有两种形式，默认是 application.properties，也可以用 application.yml：
![]({{site.url}}/img/java/springboot-07.png)

到这里，一个基本的 Spring 应用就构建完了。  
启动DemoApplication.java，用浏览器测试：
![]({{site.url}}/img/java/springboot-08.png)

>这里 json 的数据格式化推荐一个 Chrome 插件：极简 json 。非常好用！

**小结：**  

可以看到，用 Spring Boot 来开发 Spring 项目变得很方便，不需要各种复杂的 xml 文件，只需要很少的配置，就可以快速构建一个完整的项目。



**推荐阅读：**

[基于Spring Boot整合Mybatis，与数据库交互]({{site.url}}/2018/12/17/springboot-with-mybatis/)