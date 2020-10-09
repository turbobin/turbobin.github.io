---
layout:     post
title:      10. 算法篇：排序（下）
subtitle:   极客时间《数据结构与算法之美》学习笔记
date:       2019-02-19
author:     turbobin
header-img: img/post-bg-universe.jpg
catalog: true
category: 算法
tags:

   - [数据结构与算法]


---

## 大规模数据的排序算法

上一篇的冒泡排序、插入排序、选择排序这三种算法，他们的时间复杂度都是 O(n^2)，适合小规模的排序，如果涉及到大规模的数据排序，则需要更有效的排序算法，比如**归并排序**和**快速排序**，它们的时间复杂度为 O(nlogn)。这两种排序算法都用到了分治思想。

## 归并排序

### 归并排序的原理

核心思想：如果要排序一个数组，先把数组从中间分成前后两个部分，然后对前后两部分分别排序，再将排好序的两部分合并在一起，这样整个数组都是有序的了。

<img src="https://static001.geekbang.org/resource/image/db/2b/db7f892d3355ef74da9cd64aa926dc2b.jpg" style="zoom: 67%;" />

 归并排序其实使用的是分治算法，而分治算法一般都是用递归来实现的。分治是一种解决问题的处理思想，而递归是一种编程技巧。

### 归并排序的实现

归并排序要使用递归来实现，因此关键是要写出递推公式，伪代码如下：

```
递推公式：
merge_sort(A[p…r]) = merge(merge_sort(A[p…q]), merge_sort(A[q+1…r])), 其中 q=(p+r)/2

终止条件：
p >= r 不用再继续分解
```

merge 函数的作用，是将已经有序的数组 A[p...q] 和 A[q+1...r] 合并为一个有序的数组，并且放入 A[p...r] 中。

具体的过程如下：

申请一个临时数组 tmp，大小与 A[p…r]相同。我们用两个游标 i 和 j，分别指向 A[p…q]和 A[q+1…r]的第一个元素。比较这两个元素 A[i]和 A[j]，如果 A[i]<=A[j]，我们就把 A[i]放入到临时数组 tmp，并且 i 后移一位，否则将 A[j]放入到数组 tmp，j 后移一位。

重复此过程，最后其中一个子数组的所有数据都会放入临时数组中，另一个子数组遗留的数据只要依次加入到临时数组的末尾就可以了。然后把临时数组拷贝到原数组 A[p...r] 中。

<img src="https://static001.geekbang.org/resource/image/95/2f/95897ade4f7ad5d10af057b1d144a22f.jpg" style="zoom:67%;" />

实现代码如下：

```python
"""
归并排序
"""

def merge_sort(arr):
    n = len(arr)
    merge_sort_c(arr, 0, n-1)
    return arr

def merge_sort_c(arr, p, r):
    if p >= r:
        # 递归终止条件
        return

    q = (p+r) // 2  # 地板除，保证是整数
    # 分治递归
    merge_sort_c(arr, p, q)
    merge_sort_c(arr, q+1, r)
    # 合并两个有序数组
    merge(arr, p, q, r)

def merge(arr, p, q, r):
    tmp = []
    i, j = p, q+1
    while i <= q and j <= r:
        if arr[i] <= arr[j]:
            tmp.append(arr[i])
            i += 1
        else:
            tmp.append(arr[j])
            j += 1

    # 判断哪个子数组中有剩余数据
    start, end = (i, q) if i <= q else (j, r)
    # 将剩余数据拷贝到临时数组
    tmp += arr[start: end+1]
    arr[p: r+1] = tmp


if __name__ == '__main__':
    arr = [1, 5, 6, 2, 4, 3]
    print(merge_sort(arr))	# [1, 2, 3, 4, 5, 6]

```

### 归并排序的性能分析

**一、归并排序是否是稳定的排序算法？**

主要看 merge 函数，在合并过程中，如果数组中有值相同的元素，会顺序添加到 tmp 数组中，前后顺序不变，因此，归并排序是稳定的排序算法。

**二、归并排序的时间复杂度是多少？**

递归代码的复杂度分析有点复杂，不过根据递推公式，我们可以抽象得到时间复杂度的递推公式：

```
T(a) = T(b) + T(c) + K
```

求解 a 问题的时间复杂度，等于求解子问题 b 和 c 结果的时间复杂度之和，再加上 把 b，c 结果合并为 a 的结果消耗的时间 K。

假设对 n 个元素归并排序所需要的的时间是 T(n)，那么分解成子数组排序的时间都是 T(n/2)。而 merge 函数的时间复杂度为 O(n)，所以，套用递推公式，归并排序的时间复杂度为：

```
T(1) = C；   n=1时，只需要常量级的执行时间，所以表示为C。
T(n) = 2*T(n/2) + n； n>1
```

进一步求解为：

```
T(n) = 2*T(n/2) + n
     = 2*(2*T(n/4) + n/2) + n = 4*T(n/4) + 2*n
     = 4*(2*T(n/8) + n/4) + 2*n = 8*T(n/8) + 3*n
     = 8*(2*T(n/16) + n/8) + 3*n = 16*T(n/16) + 4*n
     ......
     = 2^k * T(n/2^k) + k * n
     ......
```

可以得到 T(n) = 2^kT(n/2^k)+kn。当 T(n/2^k)=T(1) 时，也就是 n/2^k=1，我们得到 k=log2n 。我们将 k 值代入上面的公式，得到 T(n)=Cn+nlog2n 。如果我们用大 O 标记法来表示的话，T(n) 就等于 O(nlogn)。所以归并排序的时间复杂度是 O(nlogn)。

分析归并排序可以看出，归并排序的执行效率与要排序的原始数组的有序程序无关，所以其时间复杂度非常稳定，最好、最坏、平均时间复杂度都为 O(nlogn)

**三、归并排序的空间复杂度是多少？**

归并排序因为在合并子数组结果时，申请了额外的临时数组空间，因此，归并排序并不是原地排序算法。

临时内存空间的大小最大不会超过 n 个数据的大小，因此，空间复杂度是 O(n)。

## 快速排序

### 快速排序的原理

快排用到的也是分治思想，不过和归并排序有点不一样：

1. 如果要排序数组中下标 p 到 r 之间的一组数据，我们选择 p 到 r 任意一个数据作为分区点 (pivot)。
2. 然后遍历 p 到 r 之间的数据，将小于 pivot 的数据放到左边，将大于 pivot 的数据放到右边，将等于 pivot 的数据放到中间。

3. 这样数据分成了 3 个区间。然后利用递归处理思想，分别对左右两边区间的数据重复上面过程。直到区间缩小为 1，说明所有区间都是有序了。

针对快排，同样可以写出递推公式：

```
递推公式：
quick_sort(A[p…r]) = quick_sort(A[p…q-1]) + quick_sort(A[q+1…r])

终止条件：
p >= r
```

根据递推公式，先来看下实现的伪代码：

```go
// 快速排序，A是数组，n表示数组的大小
quick_sort(A, n) {
  quick_sort_c(A, 0, n-1)
}
// 快速排序递归函数，p,r为下标
quick_sort_c(A, p, r) {
  if p >= r then return
  
  q = partition(A, p, r) // 获取分区点
  quick_sort_c(A, p, q-1)
  quick_sort_c(A, q+1, r)
}
```

这里的关键是要实现分区函数 partition，如果不考虑空间消耗，分区函数可以写的很简单：申请三个数组，一个存放小于分区点的值，一个存放等于分区点的值，一个用来存放大于分区点的值，最后将三个数组组装起来，拷贝到原数组中。

实现代码如下：

```python
# -*- coding: utf-8 -*-

"""
快速排序
"""

def quick_sort(arr):
    n = len(arr)
    quick_sort_c(arr, 0, n-1)
    return arr


def quick_sort_c(arr, p, r):
    if p >= r:
        return
    q = partition(arr, p, r)
    quick_sort_c(arr, p, q-1)
    quick_sort_c(arr, q+1, r)


def partition(arr, p, r):
    pivot = arr[r]
    X = []
    Y = []
    Z = []
    for i in range(p, r+1):
        if arr[i] < pivot:
            X.append(arr[i])
        elif arr[i] == pivot:
            Y.append(arr[i])
        else:
            Z.append(arr[i])
    arr[p: r+1] = X + Y + Z
    return len(X+Y) - 1


if __name__ == '__main__':
    arr = [6, 11, 3, 9, 8]
    print(quick_sort(arr))
```



上面的实现需要很多额外的空间，是非原地排序算法，如果要实现原地排序的快排，则需要改造 partition 函数，看下面实现：

```python
# -*- coding: utf-8 -*-

"""
快速排序，原地排序
"""

def quick_sort(arr):
    n = len(arr)
    quick_sort_c(arr, 0, n-1)
    return arr


def quick_sort_c(arr, p, r):
    if p >= r:
        return
    q = partition(arr, p, r)
    quick_sort_c(arr, p, q-1)
    quick_sort_c(arr, q+1, r)


def partition(arr, p, r):
    pivot = arr[r]
    i = p
    for j in range(p, r):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[r] = arr[r], arr[i]
    return i



if __name__ == '__main__':
    arr = [6, 11, 3, 9, 8]
    print(quick_sort(arr))
```

上面分区函数有点类似选择排序的思想，通过交换位置的方法实现元素的排序。值得注意的是，这个过程设计交换操作，因此**不是一个稳定的排序算法**（相同的元素相对的先后顺序会改变）。



这里比较一下归并排序和快速排序的区别：归并排序的处理过程是**由下到上**的，先处理子问题，然后再合并。快排正好相反，它的处理过程是**由上到下**的，先分区，然后再处理子问题。

### 快速排序的性能分析

快排也是用递归来实现的，这里假设每次分区操作，都能正好把数组分成大小接近相等的两个小区间，那快排的时间复杂度递推求解公式跟归并排序是相同的，所以时间复杂度也是 O(nlogn)，实际上，快排的时间复杂度大部分情况下都是 O(nlogn)。

比较极端的情况下，如对一个已经有序的数组使用快排排序，每次选择最后一个元素作为分区点，那每次分区得到的两个区间都是不均等的，大约需要进行 n 次分区操作，每次分区平均要扫描 n/2 个元素，这时，快排的时间复杂度从 O(nlogn) 退化成了 O(n2)。

### 如何求解无序数组中的第 K 大元素

利用快排的思想，我们可以在 O(n) 时间复杂度内求无序数组中的第 K 大元素。

对数组 A[0...n-1] 进行原地分区，将数组分成三个部分 A[0…p-1]、A[p]、A[p+1…n-1]。

如果 p + 1 = K，那么 A[p] 就是要求解的元素；如果 K > p + 1，说明 K 大元素出现在 A[p+1...n-1] 区间，再对右区间进行递归查找；同理，如果 K < p + 1，那么对左区间继续递推查找。

每次分区查找都会在一半的数组区间中，第一次遍历 n 个元素，第二次遍历 n/2次，.....依次遍历的是 n/4、n/8，直到区间缩小为 1。如果把每次分区遍历的个数加起来，就是 n+n/2+n/4+n/8+…+1 = 2n - 1。所以时间复杂度就为 O(n)。

### 总结：

归并和快排都是用的分治的思想，代码通过递归来实现，过程非常相似。理解归并排序主要是理解 merge() 合并函数，理解快排主要是理解 partition() 分区函数。

归并排序算法是一种时间复杂度比较稳定的排序算法，为 O(nlogn)。但是归并排序需要申请额外的内存空间，不是原地排序算法，空间复杂度比较高，为 O(n)。

快排 可以使用编程技巧做到原地排序，但不是稳定的排序算法，大部分情况下的时间复杂度为  O(nlogn)，极端情况下会退化到 O(n^2)，不过概率非常小。

快排可以在比较省内存的情况下做到对大规模数据的排序，因此，快排一般比归并排序应用比较广泛。