---
layout:     post
title:      一文理解 TCP 那些事儿
subtitle:   
date:       2020-10-05
author:     turbobin
catalog: true
category: 技术
tags:

   - [TCP]
---

### TCP 知识点概览

![TCP技术](https://gitee.com/turbobin_cao/images/raw/master/TCP+技术.png)

### TCP 头格式

![TCP header](https://nmap.org/book/images/hdr/MJB-TCP-Header-800x564.png)

图片来源：https://nmap.org/book/tcpip-ref.html

- 一个 TCP 连接是一个四元组（src_ip, src_port, dst_ip, dst_port），但是这里 TCP 的包是没有 IP 地址的，只有源端口和目标端口。因为 IP 地址在 IP 层封装；
- Sequence Number 是包的序号，用来解决网络包乱序（reordering）问题；
- Acknowledgement Number 就是 ACK，用于确认 SYN 包或 Fin 包已收到，用来解决不丢包问题；
- Window 就是著名的滑动窗口，用于解决流控问题；
- TCP Flag，TCP 标头标识，也是包的类型，主要用于操控 TCP 的状态机。

几个控制状态转换的 TCP 头标志：

- SYN：Synchronize Sequence Number，同步序列号消息，常用于初始化一个连接，功能之一就是在两个设备之间同步序列号；
- FIN：是一个带 FIN 比特位的消息，用于表示设备一方想要终止这个连接；
- ACK：Acknowledgement，一个确认消息，表示收到了 SYN 包或者 FIN 包。

其他：

- RST：表示重置连接。根据 TCP 规范，收到任何的发送到未侦听端口、已经关闭的连接的数据包、连接处于任何非同步状态（LISTEN,SYS-SENT,SYN-RECEIVED）并且收到的包的 ACK 在窗口外，或者安全层不匹配，都要回执以 RST 响应。可以利用 RST 包来终止掉处于 TIME_WAIT 状态的连接，其实这就是所谓的 RST 攻击了。

  > 例如，当两端设备状态不同步时（比如，两端还没建立连接，但是收到对方来一个 FIN 包），会发送一个 RST 包重置这个连接，然后对方收到一个错误：connect reset by peer。如果收到一个 RST 后还往这个连接写数据，就会收到 Broken pipe 错误。

- URG：表示有紧急数据要处理

- ECE：表示有拥塞

### TCP 状态机

TCP 的“连接”并不是真正意义上的连接，只不过是从没有连接的空状态，经过一系列状态变换直到变成连接状态。然后一直保持在该状态，直到收到断开连接的信号，然后再次经过一系列状态变换直到变为关闭状态。

TCP 有限状态机(Finite State Machine, FSM) 示意图如下所示：

![img](http://www.tcpipguide.com/free/diagrams/tcpfsm.png)

| 状态         | 说明                                                         | 事件与转换                                                   |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| CLOSED       | 这是每个连接开始时的默认状态。此状态表示设备之间没有创建连接。 | **被动打开 Passive Open** ：服务器通过被动打开 TCP 端口开始建立连接，同时，设置管理连接所需的数据结构（传输控制块 TCB）。然后转换为 LISTEN 状态。<br />**主动打开 Active Open**：客户端通过发送 SYN 开始建立连接，并为此建立 TCB，然后，它转换为 SYN-SENT 状态。 |
| LISTEN       | 服务器等待接收客户端同步（SYN）消息。                        | 服务器接收到客户端 SYN，然后发送 SYN + ACK，服务器进入 SYN-RECEIVED 状态。 |
| SYN-SENT     | 客户端已发送 SYN 消息，并等待服务器对应返回的 SYN            | 1. 如果客户端收到服务器的 SYN，但未收到它的 ACK，这时候会发送 ACK，并进入 SYN-RECEIVED 状态；<br />2. 如果客户端同时收到服务器的 SYN+ACK，它将发送一个 ACK，然后直接进入到 *ESTABLISHED* 状态。 |
| SYN-RECEIVED | 服务器已经收到 SYN 消息，然后发送完了自己的 SYN，现在等待对方的的 ACK 来完成连接设置。 | 客户端或服务器收到对方发来的对其 SYN 的 ACK 时，它将转换为 *ESTABLISHED* 状态。 |
| ESTABLISHED  | 开放 TCP 连接中的“稳定状态”，一旦交互的两个设备都进入这个状态，就可以自由的交互数据，这个状态将一直保持，直到其他原因被关闭为止。 | 1. 关闭，并发送 FIN：客户端可以通过发送 FIN 的位消息来关闭连接，此时将转换到 FIN-WAIT-1 状态；<br />2. 接收 FIN：服务器可能会接收到连接的客户端发来的 FIN 消息，要求关闭连接，这时，服务器将确认此消息，并转换到 CLOSE-WAIT 状态。 |
| CLOSE-WAIT   | 服务器收到客户端的 FIN 请求，现在正等待应用关闭，然后发送 FIN。 | 使用 TCP 的应用程序在被告知另一个进程想要关闭之后，会向它正在运行的机器上的 TCP 层发送一个关闭请求。然后，TCP 应用程序向已经请求终止连接的远程设备发送 FIN。这时，服务器转换到 LAST-ACK 状态。 |
| LAST-ACK     | 服务器已经接收到关闭请求并确认，然后发送自己的 FIN，这时正在等待客户端的 ACK 确认标识。 | 如果服务器发送了关闭请求(发送了 FIN) ，并且收到了客户端返回了 ACK 确认，那么就直接进入到 CLOSE 状态。 |
| FIN-WAIT-1   | 处于此状态的客户端已经发送了 FIN，正等待对方的 ACK 的确认，或者正等待其他连接的终止请求 | 1. 如果客户端发送了 FIN，已经收到了服务器返回的关闭请求的 ACK 确认，这时将转换到 FIN-WAIT-2 状态；<br />2. 如果没有收到 ACK ，但是收到了其他另一个设备的 FIN 关闭请求，这时将发送一个 ACK 给对方，然后进入 CLOSING 状态。 |
| FIN-WAIT-2   | 处于这种状态的设备收到连接终止请求的 ACK 确认，现在等待对方返回的 FIN 请求。 | 如果收到了服务器的 FIN 标识，这时将回复一个 ACK，然后进入 TIME-WAIT 状态。 |
| CLOSING      | 这个状态表示收到了其他设备的 FIN，并且回复了 ACK，但是还没有收到自己发送 FIN 的 ACK | 如果收到了自己发送连接关闭请求的确认，将转换到 TIME-WAIT 状态。 |
| TIME-WAIT    | 这个状态表示，客户端已经发出 FIN 请求，并且收到了服务器回复的 ACK，也收到了服务器发来的 FIN，并且回复了 ACK，这时，所有任务已完成，只能等待以确保 ACK 被接收，以防止与新的连接混合在一起。 | 进入这个状态后会设置一个定时器，过了设置的时间后将进入 CLOSE 状态。 |

结合三次握手和四次挥手来查看状态的变换：

![img](https://coolshell.cn/wp-content/uploads/2014/05/tcp_open_close.jpg)



- **为什么是三次握手**：主要是初始化 Sequence Number 的初始值。**通信双方要告知对方自己的初始序号(Init Sequence Number，ISN)**，所以叫 SYN（Synchronize Sequence Number，同步序列号）。这个序列号要作为以后数据通信的序号，以保证应用层接收到的数据不会因为网络上的传输问题而乱序。

- **四次挥手：** 如果有一方是被动的，如服务器被动等待客户端的连接关闭，那么交互就变成了四次挥手。但是因为 TCP 是全双工通信，如果两边同时发送自己的 FIN，然后同时回复 ACK，那么两边都会进入 CLOSING 状态，然后到达 TIME-WAIT 状态。

  ![img](http://www.tcpipguide.com/free/diagrams/tcpclosesimul.png)

- **如果建立连接时 SYN 超时**，如果服务端收到了客户端发来的 SYN 后回了 SYN + ACK，然后，客户端掉线了，这时连接处于中间状态，于是服务端会在一定时间内没有收到 ACK，就会重发 SYN+ACK。在 Linux 下会重发 5 次，重试的时间间隔是 1s，2s，4s，8s，16s，总共 31s，第 5 次发出后要等 32s 后才知道超时，所以总共需要 63s，TCP 才会断开这个连接。

- **SYN FLOOD 攻击**：一些恶意的人会利用 SYN 超时机制来制造一些无效的请求，比如发送 SYN 包后，客户端就下线了。如果大量的请求服务器，就会把 SYN 连接队列耗尽，正常的请求不会处理。为了应对这种情况，Linux 给了一个 tcp_syncookies 的内核参数，当 SYN 队列满了之后，TCP 会通过源地址端口、目标地址端口和时间戳生成一个特殊的 Sequence Number 发出去(又叫 cookie)，如果是正常请求，会把这个 cookie 发回来，服务端会通过 cookie 来建立连接；如果是攻击者，则不会有响应。tcp_syncookies 是妥协版的 TCP 协议，并不严谨，不能用它来处理大量的正常 TCP 连接请求。Linux 提供了其他几个机制供选择：1. 设置 tcp_max_syn_backlog 值来增大 SYN 连接数；2. 设置 tcp_synack_retries 来减少重试次数；3. 设置 tcp_abort_on_overflow=1，直接拒绝溢出的连接。

- **关于 ISN 初始化**：**初始序列号(ISN)不能直接 hard code**，因为假如网络包传输了一部分，连接中途断了，TCP 重连又从设置的初始值开始给包排系列号，网络中的传输包序号就全乱了。TCP 的做法是，**ISN 会和一个假的时钟绑定在一起，这个时钟每 4 微秒 对 ISN 做 +1 操作，直到超过 2^32，然后又从 0 开始**。这样，一个 ISN 的周期是 4.55 个小时。

- **关于 MSL 和 TIME-WAIT**：MSL 全称是 Maximum segment lifetime，TCP 网络包的最大存活时间。进入到 TIME-WAIT 状态时会设置一个超时器，时间是 2*MSL（[RFC793](http://tools.ietf.org/html/rfc793) 定义了 MSL 为 2 分钟，Linux 设置成了30s）。1). TIME-WAIT 状态保证了对方有足够的时间收到 ACK，如果对方没有收到 ACK，会触发对方重发 FIN，这样，发送 ACK 给对方的时间加上收到对方 FIN 的时间刚好是 2 MSL；2). 同时 TIME-WAIT 状态确保了足够的时间让当前连接不会跟新的连接混在一起（如果连接被重用了，有些延迟收到的包会跟新连接混在一起）。

- **TIME-WAIT 数量太多怎么办**：如果在大并发短连接的情况下，会造成 TIME-WAIT 数量太多，这些连接还没有被释放，因此会消耗很多系统资源（如端口号无法释放）。当然，有一些方法解决这个问题：

  - **TIME-WAIT 重用**：设置 **tcp_tw_reuse=1**，注意，这里要同时设置 tcp_timestamps=1 才会生效。
  
  - **TIME-WAIT 快速回收**：设置 **tcp_tw_recycle=1**。这个参数打开，会假设对方开启了 tcp_timestamps，然后去比较时间戳，如果时间戳变大了，就可以回收。

    > 不同设备的 timestamp 有可能不一致，这样去比较有可能导致 TIME-WAIT 被过早回收了。
  
  - **TIME-WAIT 上限** ：设置 **tcp_max_tw_buckets**，控制 TIME-WAIT 的并发数量，默认值是 18000，如果超限，系统会把多余的 TIME-WAIT 消灭掉，然后在日志里打一个警告（time wait bucket table overflow）。这个选项可以阻止一些简单的 DoS 攻击。
  
  **使用tcp_tw_reuse和tcp_tw_recycle来解决TIME_WAIT的问题是非常非常危险的，因为这两个参数违反了TCP协议。** 如果是 HTTP 协议，可以设置一个长连接，这样可以重用一个 TCP 连接处理多个 HTTP 请求。

### TCP 的延迟确认机制

TCP 的确认号（ACK）本身不含数据段，如果对每个包进行确认，会产生大量的 ACK，消耗大量的网络带宽，因此，为了提高网络利用率， RFC 建议了一种延迟 ACK 确认机制。也就是说，在收到数据包后，不会马上回 ACK，而是延迟一段可以接受的时间，看能否把要发送给对方的数据和确认号一起带回去。

**ACK 的确认号是确认最后一个字节序，对于乱序的 TCP 分段，接收端会回复相同的 ACK 分段，只确认按序到达的最后一个 TCP 分段**。TCP 连接的延迟确认时间一般初始化为最小值 40ms，随后根据连接的重传超时时间 RTO、RTT 等参数不断调整。

### TCP 重传机制

为了保证所有的数据包都可以到达，TCP 设置了重传机制。

TCP 的确认机制是累积的，接收端给发送端的 ACK 确认，只会确认最后一个连续的包(不包含最后一个)。如，发送了 1，2，3，4，5 五份连续的数据，如果全部收到了，那么会回复 ACK=6。如果先收到了 1，2，于是 ACK 3，然后收到了 4，此时 3 还没有收到，TCP 会使用超时重传机制。

#### 超时重传机制

**Seq Num 和 ACK 是以字节数为单位，所以 ACK 的时候，不能跳着确认，只能确认最大的连续收到的包。** 不然发送端就认为之前的包都收到了。

上面的例子，如果没有收到 3，那么就不回 ACK，当发送方一段时间后发现没有收到 3 的 Ack，会重传 3，一旦收到 3 后，会回复 ACK(4)。因为只收到了 3 的 ACK，所以即使接收方收到了 4，5 的包，发送方也会认为包已经丢弃了，导致重传 4 和 5。

这种机制会有两个问题：

1. 这种机制需要等 timeout，所以效率会比较差；
2. 重传选择问题：
   - 只重传超时的包。也就是第 3 份数据；
   - 重传超时后的所有数据，即重传 3，4，5 这三份数据。

#### 快速重传机制

TCP 引入了一种快速重传（Fast Retransmit）的算法，不以时间驱动，而使用数据驱动重传：如果包没有连续到达，就确认(ACK)最后那个可能被丢了的包，如果发送方连续收到 3 次相同的 ACK（Dup ACK）就重传。

比如发送方发送了1,2,3,4,5 份数据，第 1 份先到了，于是 ack 返回 2，结果 2 因为某些原因没有收到，3 到达了，就 ack 2，后面 4、5 到达了，还是 ack 2，因为 2 还是没有收到，于是发送端收到了三次 ack=2 的确认，知道了 2 还没有到，于是马上重传 2。然后，接收端收到了 2，此时，因为 3, 4, 5 都收到了，于是 ack 回 6。

![img](https://coolshell.cn/wp-content/uploads/2014/05/FASTIncast021.png)

快速重传只解决了 timeout 问题，但是仍然面临重传选择的问题，是重传 2 包呢，还是重传 2， 3，4，5 呢？因为并不知道收到的重复 ACK 是哪些包传回来的。

#### SACK 方法

因为快速重传机制无法知道接收端有哪些非连续序号的包到达了，所以无法根据 ACK 知道要重传一个包还是多个包。

一种优化的方法叫 SACK（Selective Acknowledgment，选择确认）机制，这种方式需要在 TCP 头里加一个 SACK，汇报收到的数据段。

![img](https://coolshell.cn/wp-content/uploads/2014/05/tcp_sack_example-1024x577.jpg)

这样就可以根据回传回来的 SACK 知道哪些数据到了，哪些没有到。在 Linux 下需要通过 tcp_sack 参数打开这个功能(Linux 2.4 后默认打开)。

虽然 SACK 解决了数据包选择重传的问题，但是发送方不能完全依赖 SACK，还是要依赖 ACK ，并维护 timeout，如果后续的 ACK  没有增长，还是要把 SACK 的东西重传。

#### 重复收到数据的问题(Duplicate SACK)

Duplicate SACK 简称 D-SACK，其主要使用了 SACK 来告诉发送方有哪些数据被重复接收了。

D-SACK 使用了 SACK 的第一个段来做标志，

- 如果 SACK 的第一个段的范围被 ACK 覆盖，那么就是 D-SACK；
- 如果 SACK 的第一个段的范围被 SACK 的第二个段覆盖，那么就是 D-SACK

引入 SACK 有以下优点：

- 可以让发送方知道，是发出去的包丢了，还是回来的 ACK 丢了；
- 可以让发送方知道，是不是自己的 timeout 设置太小了，导致重传；
- 可以知道，网络上出现了先发的包后收到的情况（reordering）；
- 可以知道，网络上是不是把数据包给复制了。

### TCP 的 RTT 算法

TCP 的重传机制需要设置一个超时时间 timeout，这个值对于重传特别重要

- 设长了，重发就比较慢，丢了老半天才发，没有效率，性能差；
- 设短了，会导致可能包并没有丢就重发。导致大量有效的数据包都重传了，会增加网络拥塞。

为了动态的设置，TCP 引入了 RTT(Round Trip Time)，也就是一个数据包从发出去到回来的时间。从而更方便的设置 Timeout——RTO(Retransmission Timeout)，以让我们的重传机制更高效。

为了动态的计算这个超时时间，使重传机制更加高效，有各种算法来计算 RTO 值：

**经典算法：**

1. 首先，先采样 RTT，几下好几次的 RTT 值
2. 然后做平滑计算 SRTT(加权移动平均)，**SRTT = ( α \* SRTT ) + ((1- α) \* RTT)**
3. 计算 RTO：**RTO = min [ UBOUND,  max [ LBOUND,  (β \* SRTT) ]]**，UBOUND 是最大的 timeout 时间，上限值；LBOUND是最小的timeout时间，下限值；β 值一般在1.3到2.0之间。

这个算法有个缺点：在算 RTT 样本的时候，是用第一次发数据的时间和 ack 回来的时间做 RTT 样本值，还是用重传的时间和 ACK 回来的时间做 RTT 样本值？不管是怎么选择，总会造成会要么把 RTT 算过长了，要么把 RTT 算过短了。如下图：(a)就计算过长了，而(b)就是计算过短了。

![img](https://coolshell.cn/wp-content/uploads/2014/05/Karn-Partridge-Algorithm.jpg)

**Karn / Partridge Algorithm：**

这个算法对经典算法进行了改进，最大的特点是：忽略重传，不把重传的 RTT 做采样。

这也会导致问题：如果某一时刻，网络抖动，突然变慢，产生了比较大的延时，导致所有的包都超时了，于是要重传所有的包，因为重传的不算 RTT，所以 RTO 不会被更新。这同样会导致 RTO 计算的不准确。

**Jacobson / Karels 算法：**

经典算法使用的是 “加权移动平均”，这种方法最大的毛病就是如果RTT有一个大的波动的话，很难被发现，因为被平滑掉了。所以后来又引入了一个叫 acobson / Karels Algorithm 的算法，核心思想是：除了考虑每次测量的 RTT 外，其变化率也考虑在内，如果变化率过大或过小，则通过以变化率为主的函数计算加权平均值的 RTT。如果变化率很小，则取测量平均值。

这个算法引入了最新的RTT的采样和平滑过的SRTT的差距做因子来计算。 公式如下：（其中的DevRTT是Deviation RTT的意思）

`SRTT = SRTT + α (RTT – SRTT)`  —— 计算平滑RTT

`DevRTT = (1-β)DevRTT+ β*(|RTT-SRTT|) `——计算平滑RTT和真实的差距（加权移动平均）

`RTO= µ * SRTT + ∂ * DevRTT`	——最后的公式。

在Linux下，α = 0.125，β = 0.25， μ = 1，∂ = 4 ，这个算法被用在今天的TCP协议中。

### TCP 滑动窗口

TCP 要解决的是可靠传输和包乱序(reordering)的问题，所以，TCP 需要知道网络实际的数据处理带宽或是数据处理速度，这样才不会引起网络拥塞，导致丢包。

**TCP头里有一个字段叫Window，又叫Advertised-Window，这个字段是接收端告诉发送端自己还有多少缓冲区可以接收数据**。**于是发送端就可以根据这个接收端的处理能力来发送数据，而不会导致接收端处理不过来**。

window 是一个 16 bit位的字段，代表是窗口的字节容量，大小为 2^16 - 1 = 65535 个字节。另外 TCP 的 Option 字段还包含一个 TCP 窗口扩大因子，option-kind 为 3，option-length 为 3 个字节，option-data 取值范围 0-14。窗口扩大因子用来扩大 TCP 窗口，可把原来 16bit 的窗口，扩大为 31bit。

#### 流量控制

接收方在给发送端的 ACK 中会汇报自己的 窗口大小，发送方维护一个一样大小的发送窗口，在窗口内的包可以发送，窗口外的包不能发送，窗口在发送序列上不断后移，这就是 TCP 的滑动窗口。

![img](https://coolshell.cn/wp-content/uploads/2014/05/tcpswwindows.png)

- 目录 1 表示已经发送，并收到对方 ack 确认的数据；
- 目录  2 表示已经发送但还没有收到 ack 的数据；
- 目录 3 表示在窗口中还没有发送的包（接收方还有空间）；
- 目录 4 表示接收方没有空间了，不允许发送的部分

**目录 2 + 目录 3 就是发送滑动窗口。**

如图所示，假如收到了 36 的 ACK，那么窗口向后滑动 5 个 byte

![image-20200917234941351](https://gitee.com/turbobin_cao/images/raw/master/image-20200917234941351.png)

![image-20200917235025278](https://gitee.com/turbobin_cao/images/raw/master/image-20200917235025278.png)

#### 零窗口问题

发送端的窗口是由接收端控制的。

![img](http://www.tcpipguide.com/free/diagrams/tcpswflow.png)

由上图可知，当接收端通知一个 0 窗口时，发送端的发送窗口也变成了 0，那么发送端就不能发送数据了，只能一直等待，直到再次受到接收端的通知。这种方式太依赖接收端了，如果一直不通知，那么发送端就一直干等。

为了解决 0 窗口的问题， TCP 使用了 Zero Window Probe 技术（ZWP），发送端窗口变成 0 后，会发 ZWP 包给接收方，来探测目录接收方的窗口大小，一般会间隔 30~60s 发送 3 次，如果 3 次之后还是 0 窗口的话，有的 TCP 会 RST 这个连接。

**0 窗口攻击：** 有等待的地方就有可能出现 DDoS 攻击。攻击者可以在和 Server 端建立连接后，就像 Server 端通告一个 0 窗口，然后 Server 端就只能等待进行 ZWP，于是攻击者并发大量的 0 窗口请求，把 Server 端的资源耗尽。

#### Silly Window Syndrome

Silly Window Syndrome 翻译成“糊涂窗口综合症”。

问题描述：如果接收端处理速度太慢，来不及取走接收到的包，窗口总是很快被填满，然后向后挪几个字节，然后通知发送方，这会导致发送方窗口越来越小，导致发送方接收到几个字节的窗口后就立即发送包。

为了避免有大量小包发送的问题，有两种处理方案：1）接收端不通知小窗口；2）发送端积累一点数据再发送。

- 接收端 使用  David D Clark's 方案，如果收到的数据导致 window size 小于某个值，就 ACK 回复一个 0 窗口，阻止发送端再发数据过来。等待接收端处理完了数据之后，window size 大于等于 MSS(Max Segment Size)，或者 buffer 有一半为空，就可以通告一个非 0 窗口。

- 发送端使用一个有名的 **Nagle 算法**，延迟处理数据。Nagle 算法的规则：[1]如果包长度达到 MSS ，则允许发送；[2]如果该包含有 FIN ，则允许发送；[3]设置了 TCP_NODELAY 选项，则允许发送；[4]设置 TCP_CORK 选项时，若所有发出去的小数据包（包长度小于 MSS）均被确认，则允许发送；[5]上述条件都未满足，但发生了超时（一般为 200ms ），则立即发送。

  Nagle 算法默认是打开的，对于一些小包的场景且交互性很强的程序，为了避免延迟，需要关闭这个算法。可以在 Socket 中设置 TCP_NODELAY 选项来关闭。

  ```c
  setsockopt(sock_fd, IPPROTO_TCP, TCP_NODELAY, (char *)&value,sizeof(int));
  ```

> 网络中有个最大传输单元 MTU，以太网中 MTU 默认值是 1500（Linux 下使用 netstat -i 查看），大于 MTU 的包会有两种情况，一种是直接丢弃，另一种是进行拆分打包。除去 TCP+IP 头的 40 个字节，真正的数据传输有 1460，这个值叫做 MSS（Max Seqment Size）。TCP 的RFC 定义这个 MSS 的默认值是 536，因为 RFC 791 里规定任何一个 IP 设备最少接收 576 字节大小，而 576 减去 TCP+IP 头的 40 个字节，就是 536.

### TCP 的拥塞控制

对于网络较差的情况下，传输延时会增加，TCP 会有大量的包超时重传，很容易引发网络拥堵，这时，就要启动 TCP 的拥塞控制了。

TCP 拥塞控制主要是四个算法：**1）慢启动**，**2）拥塞避免**，**3）拥塞发生**，**4）快速恢复**。

#### 慢热启动算法 -  Slow Start

慢启动体现了一个试探的过程，刚接入网络的时候发包速度慢点，探测一下网络情况，随后再慢慢提速。

慢启动算法如下：

1. 连接建立好时，先初始化 cwnd=N，表明可以传 N 个 MSS 大小的数据；

   > cwnd 表示拥塞窗口，全称 Congestion Window。

2. 每收到一个 ACK，cwnd = cwnd + 1，呈线性上升；

3. 每当过了一个 RTT，cwnd = cwnd * 2，呈指数上升；

4. 还要一个慢启动门限 ssthresh（slow start threshold），是一个上限，当 cwnd >= ssthresh 时，就会进入“拥塞避免”算法。大多数 ssthresh 的值设置成 65535 字节。

![img](https://coolshell.cn/wp-content/uploads/2014/05/tcp.slow_.start_.jpg)

根据 RFC5681，如果 MSS > 2190 bytes，则 N = 2;如果 MSS < 1095 bytes，则 N =4; 如果 2190 bytes >= MSS >= 1095 bytes，则 N = 3；一篇 Google 的论文《An Argument for Increasing TCP's Initial Congestion Window》建议把 cwnd 初始化成了 10 个 MSS。Linux 3.0 后采用了这篇论文的建议。

#### 拥塞避免算法 - Congestion Avoidance

慢启动阶段中，当 cwnd >= ssthresh时，会进入拥塞避免阶段，这时候 cwnd 的算法如下：

1. 每收到一个 ACK，cwnd = cwnd + 1/cwnd
2. 每过一个 RTT，cwnd = cwnd + 1

这是一个线性增长，慢慢调整到网络的最佳值。

#### 拥塞发生时的算法

当发生丢包的时候，TCP 会重传报文段，TCP 认为这时出现了网络拥塞。

重传有两种方式：超时重传 和 快速重传。

- 等 RTO 超时，重传数据包，TCP 认为出现拥塞的可能性很大，反应会很强烈：
  - 调整门限值 ssthresh = cwnd/2
  - reset 自己 cwnd 的值为 1
  - 重新进入慢启动阶段
- 快速重传算法，也就是在收到 3 个相同 ACK 时开始重传。这时，TCP 认为中间部分有丢失，但是后面的包都到达了，这一般是网络轻度拥塞造成的，这时候进入快速恢复算法。TCP Reno 实现是：
  - cwnd = cwnd / 2
  - ssthresh = cwnd

#### 快速恢复算法 - Fast Recovery

快速重传和快速恢复算法一般同时使用，在进入快速恢复算法前，cwnd 已经被更新为 cwnd/2，ssthresh 已被更新为 cwnd。

快速恢复的算法步骤如下：

- cwnd = ssthresh + 3 * MSS（3 的意思是确认有 3 个数据包收到了）
- 重传 Duplicated ACK 指定的数据包
- 如果再收到 Duplicate ACK，那么 cwnd = cwnd + 1
- 如果收到新的 ACK，而不是 Duplicate ACK，那么 cwnd 重置为 ssthresh 的值，然后进入拥塞避免算法了。

**上面的算法一个比较大问题是，主要依赖 3 个重复的 ACK**。3 个重复的 ACK 不代表丢了一个包，也可能是丢了好几个包，但这个算法只会重传一个，而剩下的包只能等待 RTO 超时，超时会导致 ssthresh 减半，并且退出了 Fast Recovery 阶段，多个超时会导致 TCP 传输速率呈级数下降。

当然 SACK 或 D-SACK 可以解决上面的重传问题，让发送端知道丢了几个包。但是并不是所有的 TCP 实现都支持SACK(SACK 需要两端都支持)，所以需要一个没有 SACK 的解决方案。

**TCP New Reno 算法**

这个算法在 1995 提出来，主要是在没有SACK 的支持下改进 Fast Recover 算法。具体过程如下：

- 当发送端收到 3 个Duplicate ACK 时，重传可能丢失的那个包，然后等待接收端回复的 ACK，如果回复的是全部发送数据的 ACK，那么表示只丢了一个包，否则就是多个包丢了；
- 发送端根据回复的 ACK 判断有多个包丢失，那么发送端继续重传窗口内未被 ACK 的第一个包，知道滑动窗口发出去的包全被 ACK了才真正退出 Fast Recover 阶段。

**FACK 算法**

FACK 全称是 Forward Acknowledgment 算法，这个算法是基于 SACK 的，SACK 是使用了 TCP 扩展字段 ACK 了哪些数据收到了，哪些数据没有收到，这样发送端可以准确的把那些丢掉的包重传，而不是一个个重传，但这样可能又会增加网络拥塞。FACK 用来做重传过程中的拥塞控制。

- 这个算法会把 SACK 中最大的 Sequence Number 保存在 snd.fack 这个变量中，snd.fack 的更新由 ack 带动
- 定义个 `awnd = snd.nxt - snd.fack` (snd.nxt指向发送端滑动窗口目录 3 的第一个位置)，这样 awnd 就表示网络上的数据。
- 如果需要重传数据，那么 `awnd = snd.nxt - snd.fack + retran_data` ，也就是 awnd 是传出去的数据 + 重传的数据。
- 触发 Fast Recovery 的条件是： `((snd.fack – snd.una) > (3*MSS)) || (dupacks == 3) ) `。这样一来，就不需要等到 3 个 duplicated acks 才重传，而是只要 sack中的最大的一个数据和 ack 的数据比较长了（3个MSS），那就触发重传。在整个重传过程中cwnd不变。直到当第一次丢包的`snd.nxt<=snd.una`（也就是重传的数据都被确认了），然后进入拥塞避免机制。

### Reference

- http://www.tcpipguide.com/free/t_TCPOperationalOverviewandtheTCPFiniteStateMachineF-2.htm
- https://coolshell.cn/articles/11564.html
- https://coolshell.cn/articles/11609.html
- https://mp.weixin.qq.com/s/6LiZGMt2KRiIoMaLwx-lkQ