---
layout: post
title:  "Namespace网络互联-使用Linux Bridge"
date:   2017-05-07 14:25:36 +0800
categories: Linx Network "Linux Bridge"
---

# 概览

## Linux Namespace

## Linux Bridge

## Veth

## TAP

# 使用Veth对连接两个Namespace

同一个Linux系统下两个Namespace网络互联的最简单的方式就是使用Veth设备对(veth peer)直接连
接。

![使用Veth对连接两个Namespace]({{site.url}}/assets/img/namespace-interconnecting-with-linux-bridge/veth_peer.png)

如上图所示结构，我们需要两个Namespace：ns1和ns2，然后使用一对Veth对-veth1和veth2来连接这两
个Namespace。

1. **创建两个Namespace**

        ip netns add ns1
        ip netns add ns2
    
    命令`ip`是iproute2的入口。iproute2是一套用来管理Linux网络的工具集。其中命令`ip netns`
    是用来管理网络Namespce的。`add`是`ip netns`的子命令，用来添加一个新的
    Namespace。`ns1`和`ns2`就是新增的Namespace的名字。

    然后可以查看当前系统下所有的Namespace

        ip netns list

    可以在这个命令的输出中找到刚才新创建的两个Namespce

1. **创建veth对**

        ip link add veth1 type veth peer name veth2

    命令`ip link`是用来管理Linux虚拟连接的。后面的`add`表示创建一个新的虚拟连接，新虚拟连接
    的名字是紧跟其后的参数`veth1`。参数`type veth`则表示新创建的虚拟连接`veth1`类型是
    `veth`。`peer`表示后面的参数是关于`veth`连接的另一端的。`name veth2`表示对端veth的
    设备名为`veth2`。

    创建完成后，可以使用以下命令来查看所有的veth类型的虚拟连接：

        ip link show type veth
    
    这里的`show`和上面的`add`一样，是`ip link`命令的子命令，可以用来查看虚拟连接的信息。后
    面的`type veth`参数表示只显示veth类型的连接信息。

    如果veth对创建成功，就可以在这个命令的输出中看到如下的输出信息：

        53: veth2@veth1: <BROADCAST,MULTICAST,M-DOWN> mtu 1500 qdisc noop state DOWN mode DEFAULT qlen 1000
            link/ether 66:1e:63:5d:c1:c0 brd ff:ff:ff:ff:ff:ff
        54: veth1@veth2: <BROADCAST,MULTICAST,M-DOWN> mtu 1500 qdisc noop state DOWN mode DEFAULT qlen 1000
            link/ether f6:17:23:a8:88:f3 brd ff:ff:ff:ff:ff:ff

1. **将veth设备分别加入到各自的Namespace**

        ip link set veth1 netns ns1
        ip link set veth2 netns ns2
    
    `set`是用来设置虚拟连接属性和状态的`ip link`子命令。它后面紧跟着的参数是要设置的设备的名
    字，这里就是`veth1`和`veth2`。`netns`表示要设置的属性是Namespace，`ns1`和`ns2`则分
    别是目标Namespace的名字。

    执行完这两个命令后，再使用命令`ip link show type veth`就看不到这两个veth设备了，因为
    这个命令是查看默认Namespace下的虚拟连接，而这两个设备已经被我们分别移到Namespace `ns1`
    和`ns2`下了。

    要想查看这两个Namespace下的veth设备信息，需要在对应的Namespace来执行`ip link show`命
    令：

        ip netns exec ns1 ip link show type veth
        ip netns exec ns2 ip link show type veth
    
    `exec`是`ip netns`的另一个子命令，表示使用其后紧跟的参数所指定的Namespace来执行命令。
    这里就是`ns1`和`ns2`。Namespace名字参数后面就是要执行的命令`ip link show type 
    veth`。当然，这两个命令的输出里只能看到对应Namespace下的设备。

    `ip`命令本身也支持指定Namespace参数，所以以上命令可以简化为：

        ip -n ns1 link show type veth
        ip -n ns2 link show type veth
    
    对于本身不支持Namespace参数的命令，仍然需要通过`ip netns exec`来在指定Namespace下执
    行。

1. **在各自的Namespace中设置Veth设置的IP并启用**    

    我们可以使用命令`ip address show`来查看具体设备的协议和地址状态。对于我们创建的两个veth
    设备，具体命令就是：

        ip -n ns1 address show veth1
        ip -n ns1 address show veth2
    
    其输出分别类似：
    
        54: veth1@if53: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN qlen 1000
            link/ether f6:17:23:a8:88:f3 brd ff:ff:ff:ff:ff:ff link-netnsid 1

    和

        53: veth2@if54: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN qlen 1000
            link/ether 66:1e:63:5d:c1:c0 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    
    可以看到，此时这两个veth设备都没有IP地址，并且状态都是`DOWN`。因此，在使用它们之前，需要
    给它们指定地址，并启用。

    给网络设备添加IPv4地址的命令如下：

        ip -n ns1 address add 10.120.0.11/24 dev veth1
        ip -n ns2 address add 10.120.0.12/24 dev veth2
    
    命令中的`10.120.0.11/24`和`10.120.0.12`是设备的IPv4地址和子网掩码。`dev`参数表示后
    面紧跟的参数`veth1`和`veth2`是要设置地址的设备名字。

    接下来，使用以下命令来启用这两个设备：

        ip -n ns1 link set veth1 up
        ip -n ns2 link set veth2 up
    
    执行完以上命令以后，我们再使用`ip address show`命令查看veth设备的地址，就可以看到输出变
    为类似：

        54: veth1@if53: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP qlen 1000
            link/ether f6:17:23:a8:88:f3 brd ff:ff:ff:ff:ff:ff link-netnsid 1
            inet 10.120.0.11/24 scope global veth1
                valid_lft forever preferred_lft forever
            inet6 fe80::f417:23ff:fea8:88f3/64 scope link
                valid_lft forever preferred_lft forever

    和

        53: veth2@if54: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP qlen 1000
            link/ether 66:1e:63:5d:c1:c0 brd ff:ff:ff:ff:ff:ff link-netnsid 0
            inet 10.120.0.12/24 scope global veth2
               valid_lft forever preferred_lft forever
            inet6 fe80::641e:63ff:fe5d:c1c0/64 scope link
               valid_lft forever preferred_lft forever
    
    此时，veth设备的地址和状态都已经正常，可以开始使用了。

1. **验证Namespce之间的网络连接性**

    如果之前的操作都正常，接下来就可以在两个Namespace进行网络通信了：

        ip netns exec ns1 ping -c 5 10.120.0.12
        ip netns exec ns2 ping -c 5 10.120.0.11

### 清理实验资源

如果之前的操作出错、希望重新实验或者继续其他实验，可能需要清理操作过程中创建的资源。

根据资源之前的依赖关系，可以按照以下顺序清理。

1. **清理Veth设备**

        ip -n ns1 link del veth1

    或者

        ip -n ns2 link del veth2
    
    因为veth设备必须是成对的，`veth1`和`veth2`只要删除其一一个，另一个也就同时被删除了，就
    算它们属于不同的Namespace，所以以上两个命令只需要执行任意一个。

    如果清理veth设备时，设备还没有加入Namespace，只需要将上面命令中的`-n ns1`或者`-n ns2`
    参数去掉即可。

1. **清理Namespace**

        ip netns del ns1
        ip netns del ns2
    
    在删除Namespace时，此Namespace下管理的所有虚拟网络设备也都会自动删除，所以如果veth设备
    已经加入到Namespce中，则可以跳过单独清理veth设备的过程，直接清理Namespace。
    
    如果当前系统下所有的Namespace都不需要清理，则可以通过添加`-all`参数来一次清理所有的
    Namespace：

        ip -all netns del
    
    此时不需要再指定具体的Namespace名字。

# 使用Linux Bridge和Veth连接多个Namespace

使用Veth设备对只能连接两个Namespace，如果要让多个Namespace的网络互通，一种办法就是使用
Linux Bridge配合Veth设备使用。Veth设备对的一端仍然连接到Namespace上，而另一端连接到Linux
Bridge上。


![使用Linux Bridget和Veth连接Namespace]({{site.url}}/assets/img/namespace-interconnecting-with-linux-bridge/linux_bridge_veth.png)

基本网络结构如上图。

1. 创建Namespace

    创建Namespace的方法和前文相同：

        ip netns add ns1
        ip netns add ns2

1. 创建veth设备对

    这里需要两对veth设备对：

        ip link add veth1 type veth peer name br1-veth1
        ip link add veth2 type veth peer name br2-veth2