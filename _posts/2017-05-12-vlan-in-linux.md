---
layout: post
title:  "在Linux上使用VLan"
date:   2017-05-22 18:14:07 +0800
categories: network 
---

# 概览

在[Namespace网络互联-使用Linux Bridge]({{site.url}}/network/2017/05/07/namespace-interconnecting-with-linux-bridge.html)
中，不同网段之间的隔离是通过各个Namespace自身的路由规则来实现的。这种方式很容易在Namespace上
通过修改路由规则绕过。这里介绍通过VLan的方式来在2层对网络进行划分和隔离。

本文只会演示在同一Linux系统下，使用虚拟网络设备和Linux Bridge的VLan使用。在实际场景里，我们
都需要在交换机上进行VLan的配置，不过基本原理是类似的，本文就不再讨论交换机的内容。

**本文示例环境是CentOS 7**

## VLan

VLan可以在同一个物理网络上划分多个网络，这些网络之间在二层是隔离的。通过VLan，就可以更加灵活和
高效的使用物理网络设备。

不同VLan是通过VLan ID来区分来自于不同VLan的数据包的。VLan ID被加在标准的以太帧中，被称为
tag。

通常，VLan是配置在交换机上的。交换机的每一个端口可以配置一个VLan ID。通过端口的上行数据包会加
上VLan tag，而下行数据包则会去除tag。如果下行数据包上的tag和端口上的VLan ID不一致，会被丢弃。

本文中使用Linux Bridge作为虚拟的交换机。相应的，使用Linux中的虚拟VLan设备作为交换机的端口。

# 通过VLan连接两个Namespace

我们还是从最基本的例子开始，通过Veth直接连接两个Namespace。当然，因为这种方式只能连接两个
Namespace，实际应用中在这种情况下并没有必要进行VLan划分。

在Linux系统里，需要在一个现有的网络设备上创建一个新的VLan设备，来进行VLan的配置。这个设备的主
要作用就是对上行的数据包加上VLan tag，对下行的数据包拆除VLan tag。这里，VLan设备的上联设备
就是一对Veth设备中的一个。

## 在Namespace内部设置VLan

第一个例子是将Veth添加到Namespace中，然后在Namespace里配置VLan设备：

![使用Veth对连Namespace，在Namespace内部配置VLan]({{site.url}}/assets/img/vlan-in-linux/veth_peer.png)

首先，创建并配置好图中的Namespace和Veth设备：

    ip netns add ns1
    ip netns add ns2

    ip link add veth1 type veth peer name veth2
    ip link set veth1 netns ns1
    ip link set veth2 netns ns2

    ip -n ns1 link set veth1 up
    ip -n ns2 link set veth2 up

接下来，在Namesapce中创建VLan设备：

    ip -n ns1 link add veth1.100 link veth1 type vlan id 100
    ip -n ns2 link add veth2.100 link veth2 type vlan id 100

因为VLan也是一种虚拟网络设备，所以同样使用`ip link add`来创建。`veth1.100`和`veth2.100`
是VLan设备的名字。`link`参数后面是VLan的上联设备，这里分别是Veth设备`veth1`和`veth2`。
`type vlan`表明创建的是VLan设备。`id`后面是VLan ID，这里是`100`。

和其他网络设备一样，为了使用新创建的VLan设备，需要给它们分配IP地址并启用：

    ip -n ns1 address add 10.120.1.11/24 dev veth1.100
    ip -n ns1 link set veth1.100 up
    ip -n ns2 address add 10.120.1.12/24 dev veth2.100
    ip -n ns2 link set veth2.100 up

现在，两个Namespace就可以通过VLan进行通信了：

    ip netns exec ns1 ping -c 5 10.120.1.12

### 验证

为了验证VLan设置是否生效，可以使用`tcpdump`来抓取和分析数据包的内容。

如果没有`tcpdump`工具，对于CentOS系统，可以使用`yum`进行安装：

    yum install -y tcpdump

在其中一个Namespace上持续ping另一个Namespace：

    ip netns exec ns1 ping 10.120.1.12 > /dev/null &

然后在Namespace中使用`tcpdump`：

    ip netns exec ns1 tcpdump -e -i veth1

`tcpdump`的第一个参数`-e`表示在输出中显示链路层的包头信息。因为VLan Tag是作用在2层的，所以
需要此参数来显示VLan ID。`-i veth1`表示在网络设备`veth1`上抓取所有数据包。因为VLan设备
`veth1.100`会进行VLan Tag的封装和拆除，所以在VLan设备上抓取的包是看不到VLan ID的，而需要在
VLan设备的上联设备上进行抓包。

此时，`tcpdump`会输出如下的抓包信息：

    17:48:38.427545 66:65:9c:85:35:70 (oui Unknown) > 56:b2:66:25:20:3f (oui Unknown), ethertype 802.1Q (0x8100), length 102: vlan 100, p 0, ethertype IPv4, host-192-168-0-60 > 10.120.1.12: ICMP echo request, id 27371, seq 12, length 64

其中，`vlan 100`就是指此数据包上的VLan ID是100。

## 直接使用Veth 

在当前这个例子中，Veth设备是直接分配给Namespace里的，虽然Namespace里在Veth设备上添加了
VLan，但实际上这些Veth设备仍然是可以直接使用的。

在给Veth设备分配IP地址后：

    ip -n ns1 address add 192.168.100.11/24 dev veth1
    ip -n ns2 address add 192.168.100.12/24 dev veth2

就可以直接使用Veth设备进行通信了：

    ip -n ns1 ping -c 5 192.168.100.12

## 在Namespace之外设置VLan

在上一个例子中，Veth设备被直接分配给Namespace，然后在Namespace中配置VLan。这么做的问题就是
在Namespace中Veth设备仍然可以直接使用，原本希望通过VLan来实现的网络隔离就会不可靠。另外，在
Namespace内部分别配置VLan，不利于网络配置的集中管理。

接下来，我们对这一方案进行改进，在Namespace之外创建配置好VLan设备，然后让Namespace直接使用
VLan设备。结构如下图：

![使用Veth对连Namespace，在Namespace外部配置VLan]({{site.url}}/assets/img/vlan-in-linux/veth_peer_vlan_out_namespace.png)

首先，创建图中的Namespace和Veth设备：

    ip netns add ns1
    ip netns add ns2

    ip link add veth1 type veth peer name veth2

    ip link set veth1 up
    ip link set veth2 up

接下来，直接创建VLan设备并将VLan设备分配给Namespace：

    ip link add veth1.100 link veth1 type vlan id 100
    ip link add veth2.100 link veth2 type vlan id 100

    ip link set veth1.100 netns ns1
    ip link set veth2.100 netns ns2

在Namespace中给VLan设备分配IP地址并启用：
    ip -n ns1 address add 10.120.1.11/24 dev veth1.100
    ip -n ns2 address add 10.120.1.12/24 dev veth2.100
    ip -n ns1 link set veth1.100 up
    ip -n ns2 link set veth2.100 up

此时，Namespace之间就可以互通了：

    ip netns exec ns1 ping -c 5 10.120.1.12

在这种情况下，Namespace中只有VLan设备可用，所以所有的数据包都会通过VLan进行隔离。后面所有的
例子都会采用这种方式。

# 在Linux Bridge上使用VLan

接下来，我们在Linux Bridge使用VLan来对多个Namespace的网络进行划分和隔离。

## 相同网段的两个VLan

连接在同一个linux Bridge上的网络设备默认二层是互通的，所以在默认的路由设置下，同一个网段的多个
网络设备是互通的。这里，我们为了演示VLan的隔离性，将多个Namespace连接到同一个Linux Bridge
上，并将它们设置为同一个网段，但分属两个不同的VLan：

![同一个Linux Bridge上同一网段的两个VLan]({{site.url}}/assets/img/vlan-in-linux/linux_bridge_with_vlan.png)

创建并启用Linux Bridge:

    ip link add br1 type bridge
    ip link set br1 up

创建Veth设备对:

    ip link add veth1 type veth peer name br1-veth1
    ip link add veth2 type veth peer name br1-veth2
    ip link add veth3 type veth peer name br1-veth3
    ip link add veth4 type veth peer name br1-veth4

将Veth设备对中的一端连接到Linux Bridge:

    ip link set br1-veth1 master br1
    ip link set br1-veth2 master br1
    ip link set br1-veth3 master br1
    ip link set br1-veth4 master br1

    ip link set br1-veth1 up
    ip link set br1-veth2 up
    ip link set br1-veth3 up
    ip link set br1-veth4 up

使用Veth设备对中的另一端作为VLan设备的上联设备:

    ip link add veth1.100 link veth1 type vlan id 100
    ip link add veth2.100 link veth2 type vlan id 100
    ip link add veth3.200 link veth3 type vlan id 200
    ip link add veth4.200 link veth4 type vlan id 200

    ip link set veth1 up
    ip link set veth2 up
    ip link set veth3 up
    ip link set veth4 up

创建Namespace:

    ip netns add ns1
    ip netns add ns2
    ip netns add ns3
    ip netns add ns4

将VLan设备分配给对应的Namespace:

    ip link set veth1.100 netns ns1
    ip link set veth2.100 netns ns2
    ip link set veth3.200 netns ns3
    ip link set veth4.200 netns ns4

在Namespace中给VLan设备分配IP地址，并启用:

    ip -n ns1 address add 10.120.1.11/24 dev veth1.100
    ip -n ns2 address add 10.120.1.12/24 dev veth2.100
    ip -n ns3 address add 10.120.1.13/24 dev veth3.200
    ip -n ns4 address add 10.120.1.14/24 dev veth4.200

    ip -n ns1 link set veth1.100 up
    ip -n ns2 link set veth2.100 up
    ip -n ns3 link set veth3.200 up
    ip -n ns4 link set veth4.200 up

此时，同一个VLan中的Namespace是互通的:

    ip netns exec ns1 ping -c 5 10.120.1.12
    ip netns exec ns3 ping -c 5 10.120.1.14

而不同VLan中的Namespace是不通的，虽然它们同属于`10.120.1.0/24`网段，并且不需要在
Namespace作任何额外的配置:

    ip netns exec ns1 ping -c 5 10.120.1.13
    ip netns exec ns3 ping -c 5 10.120.1.12

通过VLan，就可以很好的将连接在同一个Linux Bridge上的网络设备进行很好的进行隔离。

## 模拟网关

因为VLan会在二层进行隔离，所以如果需要将同一个Linux Bridge上的两个VLan打通，就需要一个模拟的
网关：

![同一个Linux Bridge上两个VLan之间通过模拟网关互通]({{site.url}}/assets/img/vlan-in-linux/linux_bridge_with_vlan.png)

创建并启用Linux Bridge:

    ip link add br1 type bridge
    ip link set br1 up

创建连接Namespace和Linux Bridge所需要的Veth设备:

    ip link add veth11 type veth peer name br1-veth11
    ip link add veth12 type veth peer name br1-veth12
    ip link add veth21 type veth peer name br1-veth21
    ip link add veth22 type veth peer name br1-veth22

连接Veth设备对的一端到Linux Bridge:

    ip link set br1-veth11 master br1
    ip link set br1-veth12 master br1
    ip link set br1-veth21 master br1
    ip link set br1-veth22 master br1

    ip link set br1-veth11 up
    ip link set br1-veth12 up
    ip link set br1-veth21 up
    ip link set br1-veth22 up

在Veth设备对的另一端上创建VLan设备:

    ip link add veth11.100 link veth11 type vlan id 100
    ip link add veth12.100 link veth12 type vlan id 100
    ip link add veth21.200 link veth21 type vlan id 200
    ip link add veth22.200 link veth22 type vlan id 200

    ip link set veth11 up
    ip link set veth12 up
    ip link set veth21 up
    ip link set veth22 up

创建所需的Namespace:

    ip netns add ns11
    ip netns add ns12
    ip netns add ns21
    ip netns add ns22

将VLan设备分配给对应的Namespace:

    ip link set veth11.100 netns ns11
    ip link set veth12.100 netns ns12
    ip link set veth21.200 netns ns21
    ip link set veth22.200 netns ns22

在Namespace中给VLan设备分配IP地址并启用:

    ip -n ns11 address add 10.120.1.11/24 dev veth11.100
    ip -n ns12 address add 10.120.1.12/24 dev veth12.100
    ip -n ns21 address add 10.120.2.21/24 dev veth21.200
    ip -n ns22 address add 10.120.2.22/24 dev veth22.200

    ip -n ns11 link set veth11.100 up
    ip -n ns12 link set veth12.100 up
    ip -n ns21 link set veth21.200 up
    ip -n ns22 link set veth22.200 up

如上一节所描述的一样，现在两个VLan之间是隔离的，网络无法互通。接下来，创建一个Namespace作为两
个VLan的网关。

创建用来模拟网关的Namespace:

    ip netns add nsgw

因为网关需要同时和两个VLan连接，所以需要两个Veth设备对:

    ip link add vethgw1 type veth peer name br1-vethgw1
    ip link add vethgw2 type veth peer name br1-vethgw2

将Veth设备的一端连接到Linux Bridge:

    ip link set br1-vethgw1 master br1
    ip link set br1-vethgw2 master br1

    ip link set br1-vethgw1 up
    ip link set br1-vethgw2 up

在Veth设备的另一端配置VLan:

    ip link add vethgw1.100 link vethgw1 type vlan id 100
    ip link add vethgw2.200 link vethgw2 type vlan id 200

    ip link set vethgw1 up
    ip link set vethgw2 up

将两个VLan设备都分配给网关Namespace:

    ip link set vethgw1.100 netns nsgw
    ip link set vethgw2.200 netns nsgw

在网关Namespace中将VLan设备配置为各自VLan的网关:

    ip -n nsgw address add 10.120.1.1/24 dev vethgw1.100
    ip -n nsgw address add 10.120.2.1/24 dev vethgw2.200

    ip -n nsgw link set vethgw1.100 up
    ip -n nsgw link set vethgw2.200 up

    ip -n ns11 route add default via 10.120.1.1 
    ip -n ns12 route add default via 10.120.1.1 
    ip -n ns21 route add default via 10.120.2.1 
    ip -n ns22 route add default via 10.120.2.1 

在Namespace中开启IPv4网络转发:

    ip netns exec nsgw sysctl -w net.ipv4.ip_forward=1

现在，两个VLan之间就可以互通了:

    ip netns exec ns11 ping -c 5 10.120.2.21

# 小结

本文介绍了VLan的基本概念和在虚拟网络设备上的用法。通常VLan是在物理交换机上进行配置的，不过不影
响通过虚拟网络设备来理解VLan的基本概念和特性。

对于VLan概念和使用，可以参考:

- [VLAN Support in Linux](http://www.linuxjournal.com/article/10821)
- [Linux实现的IEEE 802.1Q VLAN](http://blog.csdn.net/dog250/article/details/7354590)

本文主要是使用iproute2来对虚拟VLan ID来操作的。对于iproute2的使用，可以参考:

- [Baturin's iproute2 Doc](http://baturin.org/docs/iproute2/)
