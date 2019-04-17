---
layout:     post
title:      躺坑之路之 Nginx + uWSGI + Django 部署
subtitle:   
date:       2019-03-29
author:     turbobin
header-img: img/post-bg-desk.jpg
catalog: true
tags:

   - [Python,Django]


---

> 一篇旧文笔记，当时部署的时候还是遇到许多坑的，特别是生产环境没有联网的情况下，现在修正了一些内容，在此分享一下。

### 一、上传需要用到的包到 /home/install 下  

Python-3.6.5.tgz  (获取：https://www.python.org/ftp/python/3.6.5/)  

Django-2.0.6.tar.gz（官网下载，生产环境下一般使用源码安装）

uwsgi-2.0.17.1.tar.gz （官网下载）

nginx-1.14.0.tar.gz  （官网下载）

#### 安装依赖（可选）

若跳过这一步，可能在使用 python3.6 解释器的 virtualenv 中， pip 安装第三方包会失败。

如果是 Centos 系统，需要先安装如下依赖：

```shell
$ sudo yum -y install openssl-devel bzip2-devel expat-devel gdbm-devel readline-devel sqlite-devel gcc gcc-c++
```

也可以先使用如下命令检查是否存在上述包，如：

```shell
$ rpm -qa|grep openssl-devel
```

如果上面一些依赖没有安装，在下面的操作中会出现许多奇怪的问题。如缺少`openssl-devel`包，Python 与 uWSGI通信会有问题，缺少`sqlite-devel`包则无法操作 sqlite 数据库，缺少`readline-devel`则在 Python 命令行下无法使用键盘方向键等等。

**如果是在生产环境非联网状态下，强烈建议联系运维人员挂载一个iso镜像文件作为本地yum源。**

若是 ubuntu 系统，可通过 apt 安装以下依赖： 

```shell
$ sudo apt install build-essential checkinstall 
$ sudo apt install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
```

### 二、安装python 3.6， 在 /home/install 下依次执行以下命令：

```shell
$ mkdir python3.6
$ tar xfz Python-3.6.5.tgz -C /home/src/
    # 这里使用xfz命令，而不建议使用-zxvf命令，因为其释放的文件夹需要root权限才可以更改或者删除。
$ cd /home/src/Python-3.6.5
$ ./configure --prefix=/usr/local/python3.6
$ make altinstall
    # make altinstall 用于防止替换默认的python二进制文件/ usr / bin / python。
```

遇到权限问题加上`sudo`，以下命令类同，不做重复说明。

------

**如果是没有外网状态下，上述依赖没有安装，可能会遇到以下问题**  

参考: [Python 3 源码安装及问题解决](https://xu3352.github.io/python/2018/05/15/python-3-install)

#### SSL问题  

- 手动安装 openssl-1.0.2e:

```shell
$ cd /tmp
$ wget http://www.openssl.org/source/openssl-1.0.2e.tar.gz
$ tar xzvf openssl-1.0.2e.tar.gz
$ cd openssl-1.0.2e
$ ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl
$ make && make install
```

- 修改 ./setup.py: (默认的openssl路径不改也可以)

```python
 # Detect SSL support for the socket module (via _ssl)
 search_for_ssl_incs_in = [
                       '/usr/local/openssl/include', # 修改为新目录
                       '/usr/local/openssl/include/openssl',  # 新增
                       '/usr/contrib/ssl/include/'
                      ]
```

- 修改 ./Modules/Setup.dist

```python
# Socket module helper for socket(2)
_socket socketmodule.c  # 取消注释

# Socket module helper for SSL support; you must comment out the other
# socket line above, and possibly edit the SSL variable:
SSL=/usr/local/openssl   # 这里改为我们指定的目录
_ssl _ssl.c \
    -DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \
    -L$(SSL)/lib -lssl -lcrypto
```

- 最后重新 `make altinstall`编译安装

#### zlib问题

**如果安装出现 "zipimport.ZipImportError: can't decompress data; zlib not available"** 

按以下步骤解决：

```shell
$ cd python3.6/Python-3.6.5/Modules/zlib
$ ./configure
$ make install
$ cd -
$ make altinstall   # 回到Python-3.6.5下重新编译安装
```

---

安装成功后，建立python3.6的软连接（一般 linux 自带 python2 版本，注意不要覆盖了原有的 python 命令）

```
$ ln -s /usr/local/python3.6/bin/python3.6  /usr/bin/python3
```

同样建立 pip3.6 的软连接并升级pip（执行前先检查一下是否有其他版本的 pip，使用`pip -V`命令检查版本）

```shell
$ ln -s /usr/local/python3.6/bin/pip3.6  /usr/bin/pip
$ pip install --upgrade pip --user（联网环境下）
# 遇到权限问题 加上 --user
```

将python3.6/bin 加到环境变量

```shell
$ vi ~/.bashrc
# 在最后添加:
PATH=/usr/local/python3.6/bin:$PATH:$HOME/bin
export PATH
# 保存退出，使环境变量生效
source ~/.bashrc
```

### 三、安装Django和Uwsgi

解压 Django-2.0.6.tar.gz 和 uwsgi-2.0.17.1.tar.gz

```shell
tar -zxvf Django-2.0.6.tar.gz
tar -zxvf uwsgi-2.0.17.1.tar.gz
# 安装Django
cd Django-2.0.6
 python setup.py install # 等待安装完毕
# 安装uwsgi
cd uwsgi-2.0.17.1
sudo python setup.py install
```

**2018.9.28更新：**

**忽略以上方法，采用更简便的方法安装 -->安装好python之后，直接使用 `pip install Django-2.0.6.tar.gz`即可安装，uwsgi 同理。**  

**提示：安装 Django 前需要先安装 pytz 依赖包:`pip install pytz-2018.5.tar.gz`**

#### 注意事项

如果采用python虚拟环境来安装：

- 建立python虚拟环境:  

  ```
  python3 -m venv django_venv
  或
  virtualenv django_venv # 需要先 pip install virtualenv
  ```

- 激活虚拟环境 

  `source django_venv/bin/activate`

- 接下来可以使用python 和 pip命令了，只在当前虚拟环境有效

  **注意：如果使用pip 安装出现`Permission denied 没有权限`，此时不要加上sudo 或 --user来安装，否则会安装在系统python下，不会安装到虚拟环境中。此时的解决办法是，更改虚拟环境目录文件夹拥有者。**

  **使用 `ls -l` 可以查看到当前目录和文件所属用户是root， 使用以下命令更改成当前用户：`sudo chown -R turbobin:turbobin django_venv`**

### 四、Django项目静态文件设置

```python
STATIC_URL = '/static/'

# 我的设置
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

在 `manage.py` 同级目录下创建`collected_static`文件夹,同时新建`static`空文件夹

收集所有app下的静态文件，方便nginx配置。

执行命令：

```shell
python manage.py collectstatic
```

### 五、配置uwsgi启动Django项目

1. 上传 Django 项目源码到 /usr/local/src 下
2. 我的项目目录树：

```
└── ykd-web
    ├── static
    ├── collected_static
    │   ├── admin
    │   ├── css
    │   ├── fonts
    │   ├── img
    │   ├── js
    ├── manage.py
    ├── khyx_web
    │   └── database_router.py
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── positions
    │   ├── migrations
    │   ├── static
    │   |   ├── css
    │   |   ├── fonts
    │   |   ├── img
    │   |   ├── js
    │   └── templates
    └── users
```

3. 执行必要的迁移

```shell
python3 manage.py makemigrations
python3 manage.py migrate --database=db01   # 我使用了两套数据库，且设置了数据库路由
python3 manage.py migrate	# 默认执行 default 配置的数据库
```

4. 首先使用Django自带服务器运行django项目,确保能正常工作

```
python manage.py runserver 192.168.180.130:8000
 # 此地址为服务器地址，现在可以使用本地window浏览器打开网址
```

如果正常，则使用uWSGI来运行它:  

`uwsgi --http :8000 --module khyx_web.wsgi`  

Tips：如果8000端口被占用，可以选择杀死进程或选择其他端口

```
lsof -i:8000    # 查看端口占用
或按照程序名称查询：
ps aux | grep uwsgi

kill -9 [PID]  / killall -9 uwsgi # 强迫进程停止
```

现在可以在ubuntu浏览器上访问`http://127.0.0.1:8000/ykd-web/`  

但是访问发现没有加载样式，下面使用nginx来处理静态文件

5. 配置uwsgi.ini文件来简化上面的uwsgi命令  

   创建uwsgi.ini文件

```shell
$ cd /usr/local/src/ykd-web
$ vi uwsgi.ini
```

写入以下内容：

```ini
# uwsgi.ini file

[uwsgi]

# Django-related settings
#http = 192.168.180.130:8000
# the base directory (full path)

chdir = /usr/local/src/ykd-web

# Django s wsgi file
module = khyx_web.wsgi

# 新建一个空白的reload文件，只要输入' touch reload'项目就会重启
touch-reload = /usr/local/src/ykd-web/reload
# process-related settings

# master
master = true

# listen
listen = 1000 # 并发的socket 连接数。默认为100。优化需要根据系统配置

# maximum number of worker processes
processes = 4
workers = 10  # 并发处理进程数

# the socket (use the full path to be safe
# 等下把sock和nginx关联起来
socket = /usr/local/src/ykd-web/khyx_web.sock
# socket=:8000

# ... with appropriate permissions - may be needed
chmod-socket = 666
#chown-socket = ykd-web:www-data
# clear environment on exit
vacuum = true

# log file
daemonize = /usr/local/src/ykd-web/log/run.log
disable-logging = true  // 不记录正常信息，只记录错误信息
```

详细说明：

- 配置项中以`‘#’`开头的都是被注释的项目，不起作用；
- 以双斜杠开头，表示注释；
- chdir是你的项目根目录。我这里的项目名叫 ykd-web；
- moudule是你的入口wsgi模块，将 ykd-web 替换成你的项目名称；
- socket是通信端口设置，可以使用 sock 文件，也可以使用端口号与 Nginx 通信；
- master=True 表示以主进程模式运行；
- demonize 是你的日志文件，会自动建立
- disable-logging = true 表示不记录正常信息，只记录错误信息。否则你的日志可能很快就爆满了。  

另参考:[uwsgi配置详解](http://www.voidcn.com/article/p-tutitumn-re.html)。

输入`uwsgi --ini uwsgi.ini`来启动项目  

**问题一：**

此时可能会遇到 `bind(): Permission denied [core/socket.c line 230]`, 可以将sock文件或者所在文件夹权限设置大一点。

**问题二：**

在做优化之前，发现并发数过不了100，因为 uwsgi 的socket 默认链接为100。修改`listen = 1000` 发现无法启动，此时查看系统限制连接数：

```shell
$ ulimit -n
65535
```

再查看系统配置文件` vi /etc/sysctl.conf`，添加内容：

```shell
# 定义了系统中每一个端口最大的监听队列的长度,这是个全局的参数,默认是128.
net.core.somaxconn = 2048
```

运行`sysctl -p` 命令使配置生效。

### 六、Nginx的安装与配置

#### 安装Nginx

有条件可以直接联网安装（不建议）：
`sudo apt install nginx`  

否则参考以下步骤：  
https://www.cnblogs.com/wyd168/p/6636529.html

1.安装PCRE库

```shell
cd /home/install
wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.42.tar.gz # 预先下载上传服务器
tar -zxvf pcre-8.42.tar.gz -C /home/src/
cd /home/src/pcre-8.34
./configure	# 默认安装到 /usr/local/bin 下
make
make install
```

2.安装zlib库（可选，上面 python 问题解决 zlib 问题可能已安装）

```shell
cd /home/install 
wget http://zlib.net/zlib-1.2.11.tar.gz
tar -zxvf zlib-1.2.11.tar.gz -C /home/src
cd /home/src/zlib-1.2.11
./configure
make
make install
```

3.安装openssl（某些 vps 默认没装ssl) （可选，上面 python 解决 ssl 问题时可能已安装）

```shell
cd /home/install
wget https://www.openssl.org/source/openssl-1.0.1e.tar.gz
tar -zxvf openssl-1.0.1e.tar.gz -C /home/src/
cd /home/src/openssl-1.0.1e
./configure
make
make install
```

4.安装nginx

```shell
cd /home/install
tar -zxvf nginx-1.14.0.tar.gz -C /home/src
cd /home/src/nginx-1.14.0
./configure --prefix=/usr/local/nginx --with-http_stub_status_module --with-http_ssl_module --with-pcre=/home/src/pcre-8.42 --with-zlib=/home/src/zlib-1.2.11 --with-openssl=/home/src/openssl-1.0.1e
make
make install
```

#### 配置Nginx

1.新建一个网站配置文件  

` vi /usr/local/nginx/sites-available/ykd_web.conf`

写入以下内容：

```nginx
server {
    listen      8001;
    server_name 192.168.180.130; # 如果购买了域名也可填你的域名
    charset     utf-8;
 
    client_max_body_size 75M;

    location /static {
        alias /usr/local/src/ykd-web/collected_static;
    }
 
    location / {
        uwsgi_pass  unix:///usr/local/src/ykd-web/khyx_web.sock;
        include     /etc/nginx/uwsgi_params;
        
         # when a client closes the connection then keep the channel to uwsgi open.Otherwise uwsgi throws an IOError
        uwsgi_ignore_client_abort on;
        
        uwsgi_send_timeout 600;        # 指定连接到后端uWSGI的超时时间。
        uwsgi_connect_timeout 600;     # 指定向uWSGI传送请求的超时时间，完成握手后向uWSGI传送请求的超时时间。
        uwsgi_read_timeout 600;        # 指定接收uWSGI应答的超时时间，完成握手后接收uWSGI应答的超时时间。
    }
}
```

2.激活网站：

```shell
$ ln -s /usr/local/nginx/sites-available/ykd_web.conf /usr/local/nginx/sites-enabled/ykd_web.conf
```

> 注：如果是源码安装的nginx，可能没有sites-available,sites-enabled文件夹，此时可以将配置文件内容直接写入nginx.conf，或者在nginx.conf加上 `'include /usr/local/nginx/site-enabled/*;'` 然后创建sites-available，sites-enabled文件夹（推荐）

3.启动nginx：

`sudo /usr/local/nginx/sbin/nginx` （Centos）

`sudo /etc/init.d/nginx start` 	(ubuntu)

查看nginx是否启动：

`ps -ef|grep nginx`  

重启nginx：

`sudo /usr/local/nginx/sbin/nginx -s reload`	（Centos）

`sudo /etc/init.d/nginx restart`	(ubuntu)

4.此时再启动 uwsgi

```shell
cd /usr/local/src/ykd-web
uwsgi --ini uwsgi.ini
```

5.在window本地访问 http://192.168.180.130:8001  
如有报错，可查看日志文件:

> vi /usr/local/nginx/logs/access.log  # 访问日志 （Centos）
>
> vi /usr/local/nginx/logs/error.log # 报错日志文件
>
> 或
>
> vi /var/log/nginx/error.log  # 报错日志文件  （ubuntu）
>
> vi /var/log/nginx/access.log # 访问日志

6.其他问题：

如果用的sqlite3数据库文件，发现数据库没有写权限，使用以下命令提升权限：

```shell
cd /usr/lcoal/src/ykd-web
sudo chmod 777 db.sqlite3   # 不安全，可改成666
```

修改之后发现报以下错误：  

`unable to open database file`  

Django官方文档解释：  

`Django says “Unable to Open Database File” when using SQLite3`  
`Problem`  
`You’re using SQLite3, your DATABASE_NAME is set to the database file’s full path, the database file is writeable by Apache, but you still get the above error.`  
`Solution`  
`Make sure Apache can also write to the parent directory of the database. SQLite needs to be able to write to this directory.`  
`Make sure each folder of your database file’s full path does not start with number, eg. /www/4myweb/db (observed on Windows 2000).`   
`If DATABASE_NAME is set to something like ‘/Users/yourname/Sites/mydjangoproject/db/db’, make sure you’ve created the ‘db’ directory first.`
`Make sure your /tmp directory is world-writable (an unlikely cause as other thing on your system will also not work). ls /tmp -ald should produce drwxrwxrwt ….`  
`Make sure the path to the database specified in settings.py is a full path.`  

大概就是说用户访问的是数据库文件的全路径，需要把包含数据库文件的文件夹也赋予读写权限

### 七、配置自启动的uwsgi

nginx会在Linux启动时自行启动，而uwsgi需要手动启动，修改了uwsgi.ini时也需要重启服务，下面来配置自启动的uwsgi

#### Emperor模式

uWSGI可以运行在‘emperor’模式。在这种模式下，它会监控uWSGI配置文件目录，然后为每个它找到的配置文件生成实例 (‘vassals’)。

每当修改了一个配置文件，emperor将会自动重启 vassal.

```shell
# create a directory for the vassals
sudo mkdir /etc/uwsgi
sudo mkdir /etc/uwsgi/vassals
# symlink from the default config directory to your config file
sudo ln -s /usr/local/src/learning_log/uwsgi.ini  /etc/uwsgi/vassals/learning_log.ini
sudo ln -s /usr/local/src/ykd-web/uwsgi.ini       /etc/uwsgi/vassals/ykd_web.ini
# run the emperor
uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data
```

选项表示:

- emperor: 查找vassals (配置文件)的地方
- uid: 进程一旦启动后的用户id
- gid: 进程一旦启动后的组id  

这里启动了两个Django项目下的站点。检查站点；它应该在运行。

#### 系统启动时运行uWSGI

最后一步是让这一切在系统启动的时候自动发生。

对于许多系统来说，最简单 (如果不是最好的)的方式是使用 rc.local 文件。

```shell
$ sudo mkdir /var/log/uwsgi
```

编辑 /etc/rc.local 然后在”exit 0”行前添加:

```shell
$ /usr/local/python3.6/bin/uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data --daemonize /var/log/uwsgi/uwsgi-emperor.log
```

系统启动时还未加载环境变量，所以uwsgi要写绝对路径。系统默认是以root权限来运行，查看log，如果vassals下有实例启动失败，有可能是socket文件没有权限创建，或者所在文件夹归属于用户，root没有权限读写，需要更改文件目录权限。



<p>&nbsp;</p>

> 本文首发于 [turbobin's Blog](https://turbobin.github.io/) 。转载请注明出处，附上本原文链接， 谢谢合作。