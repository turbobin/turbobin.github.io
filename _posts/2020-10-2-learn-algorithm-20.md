---
layout:     post
title:      20. 数据结构篇：堆的应用
subtitle:   极客时间《数据结构与算法之美》学习笔记
date:       2020-10-02
author:     turbobin
header-img: img/post-bg-universe.jpg
catalog: true
category: 算法
tags:

   - [数据结构与算法]


---

堆有很多经典的应用，如堆排序、优先级队列、求 Top K 、求中位数

## 优先级队列

一个堆就是一个天然的优先级队列，往优先级队列中插入一个元素，就相当于往堆中插入一个元素，从优先级队列中取出一个元素，就相当于取出堆顶元素。

### 应用一：合并有序小文件

假设有 100 个小文件，每个文件的大小是 100MB，每个文件中存储的都是有序的字符串。需要将这 100 个小文件合并为一个有序的大文件。

方案一：

从这 100 个小文件中各取第一个字符串，放入数组中，然后比较大小，找出最小值，把最小的字符串放入合并后的大文件中，并将这个最小字符串从数组中删除，然后从这个最小字符串的来源文件中取第二个字符串放入数组中，再次找出最小值追加放入到大文件中。依次类推，直到所有的文件中的数据都放入到大文件中。

方案二：

这里用数组来存储每个字符串并找出最小值，每次都要遍历整个数组，显然不是很高效。这里可以用到优先级队列：维护一个小顶堆，堆顶的元素就是存储的最小字符串，每次只需要取出堆顶的元素放入到大文件中，然后再从小文件中取出下一个字符串插入到堆中，循环这个过程，就可以依次将所有的字符串有序的添加到大文件中。

在数组中找出最小值的时间复杂度为 O(n)，而往堆中插入或删除一个元素的时间复杂度为 O(logn)，所以，第二种方案会更高效。

### 应用二：高性能定时器

假设有一个定时器，维护了很多的定时任务。常规做法是，定时器每过 1 秒扫描一遍任务，看是否有任务到达执行时间。

但是，这种做法比较低效。第一，任务的定时时间可能离当前还有很久，每个一秒就扫描会对系统造成很大负载；第二，如果任务列表很大，任务执行密度很大，扫描会比较耗时，势必会影响任务的执行。

这些问题可以使用优先级队列来解决。按照任务的设定时间，将这些任务存储在优先级队列中，队首就是小顶堆的堆顶，即最先执行的任务。只要拿队首任务的时间点与当前时间相减，得到一个时间间隔 T，那么定时器只需要等待 T 秒后执行队首任务就可以了。之后再重新计算队首任务的时间间隔。

## 求 Top K

我们可以一直都维护一个 K 大小的小顶堆，当有数据被添加到集合中时，我们就拿它与堆顶的元素对比。如果比堆顶元素大，我们就把堆顶元素删除，并且将这个元素插入到堆中；如果比堆顶元素小，则不做处理。这样，无论任何时候需要查询当前的前 K 大数据，我们都可以立刻返回前 K 大元素。

## 求中位数

对于一组静态数据，中位数是固定的，我们可以先排序，第 n/2 个数据就是中位数。每次询问中位数的时候，我们直接返回这个固定的值就好了。

如果是动态数据，每次去排序，代价就比较大了。而借助堆这种数据结构，可以不用排序，实现动态的求中位数的操作。

维护两个堆，一个大顶堆，一个小顶堆。先对现有数据排序，大顶堆存储前半部分数据，小顶堆存储后半部分数据。假设有 n 个数据，如果 n 是偶数，那么大顶堆存储前 n/2 的数据，小顶堆存储后 n/2 个数据；如果 n 是奇数，那么大顶堆存储 n/2 + 1 个数据，小顶堆存储后 n/2 个数据。

这时候大顶堆的堆顶就是要找的中位数。

当动态插入一个数据时，需要调整两个堆：如果新加入的数据小于等于大顶堆的堆顶元素，就将这个数据插入到大顶堆中，否则插入到小顶堆中。如果插入后，两个堆不满足上面的数量关系，那就将比较多的那个堆的堆顶元素移到另一个堆，通过这样调整，是两个堆满足上面的数量关系规则。