---
layout:     post
title:      在Python中使用JWT
subtitle:
date:       2020-03-25
author:     turbobin
header-img:
catalog: true
category: 技术
tags:
    - Python
---

JWT 是 `Json Web Token` 的缩写。一般用于用户认证中。

互联网中，常用的用户认证方案一般有两种。

### Session认证

session 认证一般流程如下：

1、用户使用浏览器向服务器发送请求认证，带上用户ID和密码

2、服务器认证通过后保存一下用户信息，如用户ID，登录时间，并生成一个 session 会话保存在缓存或数据库中。查找 session 的 key 叫做 session_id

3、服务器把 session_id 下发给浏览器，写入用户的 cookie 或 storage 中

4、随后浏览器的每一次请求都会带上 session_id 传给服务器，服务器收到后，从缓存中查找用户信息，由此得知用户身份。

使用 session 可以方便的管理用户的状态。在集群环境中，为了保证用户请求每一台服务器都能拿到会话，因此 session 不能单独保存在每一台业务机器中，应该使用公共的缓存或数据库集中管理，保证每一台业务机器都能访问到。

Python 生成session 示例如下：

```python
import time
import hashlib
import json
import redis

now = time.time()
user_id = 12345
user_name = "turbobin"
session_id = hashlib.md5("%s%s" %(user_id, now)).hexdigest()
session_data = json.dumps({"user_id": user_id, "user_name": user_name})
redis.set(session_id, session_data, ex=24*60*60)	# 存到redis中

```

### JWT 认证

JWT 的原理是，服务器认证之后发回给用户一个 json 对象，如：

```json
{
    "user_id": 12345,
    "user_name": "turbobin",
    "expire_time": 86400
}
```

之后客户端与服务器通信的时候都要发回这个 json 对象，服务器完全只靠这个对象认证用户身份。为了防止篡改数据，服务器生成对象时会加上签名

JWT 的结构如下：

头部 + 负载 + 签名

```
Header.Playload.Signature
```

#### Header 部分 

Header 是一个 json 对象，描述 JWT 的元数据：

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

`alg`表示使用的 算法，默认是 `HMAC SHA256`，简写成 `HS256`，`type`表示 token 的类型，像 JWT 令牌统一就写成 `JWT`。

#### Playload 

Playload 也是一个 json 对象，用来存放实际需要传递的数据。JWT 规定了 7 个官方字段：

- iss (issuer)：签发人
- exp (expiration time)：过期时间
- sub (subject)：主题
- aud (audience)：受众
- nbf (Not Before)：生效时间
- iat (Issued At)：签发时间
- jti (JWT ID)：编号

除了官方字段，还可以定义私有字段，如：

```json
{
    "user_id": 12345,
    "user_name": "turbobin"
}
```

### Signature

signature 是对前两部分的签名，防止数据篡改。

签名前需要指定一个密钥 `secret`，这个密钥只有服务器知道，不能外泄出去，然后按照 Header 中指定的算法对前两部分进行签名

```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

算出签名以后，把 Header、Payload、Signature 三个部分拼成一个字符串，每个部分之间用"点"（`.`）分隔，就可以返回给用户。

Python 示例：

```python
import jwt		# 需要先 pip install pyjwt
import time

playload = {
    "user_id": 12345,
    "user_name": "turbobin",
    "exp": int(time.time()) + 5*60		# 5分钟后过期
}
secret = "fjahskljrtlkwjegoi23948nkasdjion"
# 加密
jwt_token = jwt.encode(playload, secret, algorithm='HS256')
print("jwt_tokne:", jwt_token)
# 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiJ0dXJib2JpbiIsInVzZXJfaWQiOjEyMzQ1LCJleHAiOjE1ODUxMjYzMDh9.pRIimaTYTV-dS_hTVeG1Uo9y5VqLeln9pUNzRrB180M'

# 解密也要用到 secret
data = jwt.decode(jwt_token, seret) 
# {u'user_id': 12345, u'user_name': u'turbobin', u'exp': 1585126308}
```

如果设置的 exp 过期了，`jwt.decode`时候就会抛出异常`jwt.exceptions.ExpiredSignatureError: Signature has expired`。

### 参考

[JSON Web Token 入门教程 - 阮一峰的博客](https://www.ruanyifeng.com/blog/2018/07/json_web_token-tutorial.html)






