---
layout:     post
title:      博客主题迁移与域名绑定
subtitle:   
date:       2019-04-16
author:     turbobin
header-img: img/post-bg-desk.jpg
catalog: true
category: 资源
tags:

   - [Blog]


---



### 主题更换

从四个月前开通博客以来，一直用的一款 Jekyll 的经典主题，它长这样：

![20190416233725](https://tva3.sinaimg.cn/large/9f999f0bly1g24wia61pjj21df0m94qp.jpg)

![20190416234415](https://tvax4.sinaimg.cn/large/9f999f0bly1g24wmtvzrij21dj0fxtca.jpg)

首页和文章都有图片置顶，打开文章加载特别缓慢，特别影响体验。

最近偶然间看到闫肃大大的[博客](http://yansu.org/)，发现也是基于 Jekyll + GitHub Pages 搭建的，主题简洁，文章目录一目了然，还自带了搜索功能，特别是文章字体和代码格式非常美观，于是决定弃用之前的主题了。以后写博客不用考虑每次写文章的配图了，少了很多图片的加载，文章打开加载速度就快多了，回归了写文章的初衷，体验更棒！而且在手机上打开体验也非常不错，在此感谢闫肃大大的博客，感谢原作者开发的主题 [3-Jekyll](https://github.com/P233/3-Jekyll) 。

基于 Jekyll 搭建的博客越来越少了，现在用 Hexo 搭建的比较多，原本打算用比较流行的 [Next](https://github.com/theme-next/hexo-theme-next/blob/master/docs/zh-CN/README.md) 主题，最近看到的 [Vexo](https://github.com/yanm1ng/hexo-theme-vexo) 主题也不错，但也有个别不太喜欢的地方，就暂时不去折腾安装 Hexo 了。



### 域名绑定

最近在阿里万网买了域名 `turbobin.site`，挺便宜，￥8/年，原本想买 `turbobin.com`，但是已经被人注册了，以后如果抢到了再更换吧。

域名的申请模板需要先进行实名认证，不然后面解析会显示异常。如果需要绑定阿里**国内**的云主机，还必须去申请备案才能用，不然绑定了云主机地址是无效的，备案申请是挺麻烦的，需要填一大堆的真实信息。

如果只是绑定 GitHub Pages 个人博客，就没必要去申请备案，只需要绑定博客的域名就好了。

域名绑定 GitHub Pages 也挺简单，登录阿里云控制台 -- 域名 -- 选择购买好的域名，点击解析 -- 添加记录，按如下方式填写

![20190417002003](https://tvax3.sinaimg.cn/large/9f999f0bly1g24xotnypsj217d0kfmye.jpg)

之后在 `CNAME` 文件中填写上域名就可以解析了，或者在 GitHub Pages Settings 页面也可以设置。

![20190417003016](https://tva4.sinaimg.cn/large/9f999f0bly1g24xyrlnpzj20wi0l4ab4.jpg)

之后大概等十多分钟会自动生效。



### 小结

这次折腾博客也费了不少时间，修改了很多的细节样式，比如图片的阴影效果，字体的大小，表格的样式等等，总算整成让自己满意的样子了，域名的购买与解析也走了不少弯路，网上很多教程都已经过时了，以后有时间专门写一篇总结一下购买域名的坑。总之，现在博客折腾暂时告一段落了，以后把更多的时间专注在技术知识的吸收与输出上面。



<p>&nbsp;</p>
> 本文首发于 [turbobin's Blog](https://turbobin.github.io/) 。转载请注明出处，附上本原文链接， 谢谢合作。