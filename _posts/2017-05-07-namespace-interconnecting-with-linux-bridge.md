---
layout: post
title:  "Namespace网络互联-使用Linux Bridge"
date:   2017-05-07 14:25:36 +0800
categories: Linx Network "Linux Bridge"
---

# 概览

使用软件对网络进行虚拟化是虚拟化技术的一个很重要的组成部分。通过对网络进行虚拟化，才能在不受实际
物理网络设备和拓扑限制的情况下，让虚拟机之间进行网络通信。本文介绍在同一个Linux系统下，使用
Linux Bridge和VETH设备来组建虚拟网络。

## Linux Namespace

Namespace是Linux的一个用来对系统资源进行虚拟化和隔离的功能。每个Namespace有自己的独立的进程
ID、主机名、网络访问等，可以当成一个独立的系统。在本文，一个Namespace就相当于网络上的一台电脑
或者服务器。

## Linux Bridge

Linux Bridge是一种虚拟的网络转发设备，工作在2层。一个Linux Bridge可以连接多个Linux上的网络
设备，包括物理设备和虚拟设备。它会将所有的数据转发到所有连接在它上面的设备。在本文中，我们使用
Linux Bridge在多个虚拟网络设备之间进行数据交换，类似一个基本的交换机。

## VETH

VETH设备是一种虚拟的以太网设备。它总是成对使用，就像一条网线的两端，用来分别连接两个网络设备，
来使得这两个被连接的网络设备可以通过VETH进行通信。在本文中，我们用VETH来连接Namespace和Linux
 Bridge。

 但KVM一般不能直接使用VETH设备。

## vTAP

vTAP设备是另一种虚拟网络设备，作用类似于VETH。不过vTAP是单独使用的，不像VETH需要成对使用。
vTAP会映射成一个文件描述符(file descriptor)供程序或者虚拟机使用，不能直接通过Namespace
使用。KVM使用vTAP设备来给虚拟机提供网卡设备。

vTAP设备同样可以配合Linux Bridge使用，不过为了实验简单，本文只演示VETH设备的使用。

# 使用VETH对连接两个Namespace

同一个Linux系统下两个Namespace网络互联的最简单的方式就是使用VETH设备对(veth peer)直接连
接。

![使用VETH对连接两个Namespace]({{site.url}}/assets/img/namespace-interconnecting-with-linux-bridge/veth_peer.png)

如上图所示结构，我们需要两个Namespace：ns1和ns2，然后使用一对VETH对`veth1`和`veth2`来连接
这两个Namespace。

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

1. **在各自的Namespace中设置VETH设置的IP并启用**    

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

1. **清理VETH设备**

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

# 使用Linux Bridge和VETH连接多个Namespace

使用VETH设备对只能连接两个Namespace，如果要让多个Namespace的网络互通，一种办法就是使用
Linux Bridge配合VETH设备使用。VETH设备对的一端仍然连接到Namespace上，而另一端连接到Linux
Bridge上。


![使用Linux Bridget和VETH连接Namespace]({{site.url}}/assets/img/namespace-interconnecting-with-linux-bridge/linux_bridge_veth.png)

基本网络结构如上图。

1. **创建Namespace**

    创建Namespace的方法和前文相同：

        ip netns add ns1
        ip netns add ns2

1. **创建并启用Linux Bridge**

        ip link add br1 type bridge
    
    Linux Bridge同样也是一种Linux虚拟连接，所以同样使用`ip link add`命令来创建。类型对应
    选择为`bridge`

    类似的，同样可以通过以`ip link show`和`ip link address`命令来查看Bridge的状态：

        ip link show type bridge
        ip link show br1
        ip address type bridge
        ip address show br1
    
    此时，可以看到`br1`的状态仍然是`DOWN`，所以需要使用以下命令启用：

        ip link set br1 up
    
    Bridge类似交互机，自身不需要IP地址，所以此时`br1`已经可以使用了。

1. **创建veth设备对**

    这里需要两对veth设备对：

        ip link add veth1 type veth peer name br1-veth1
        ip link add veth2 type veth peer name br2-veth2
    
    这里，veth设备的名字是可以任意的，只要在当前系统中不重复即可。为了便于区分是连接在
    Namespace上还是Bridge上，分别命名为了`veth1`和`br1-veth1`这样的模式，但实际不是必需
    的。veth设备对中哪个连接到Namespace，哪个连接到Bridge，也是可以任意选取的。

1. **连接veth设备一端到Namespace并设备地址和状态**

    将`veth1`和`veth2`分别连接到Namespace `ns1`和`ns2`，并设置地址和启用。它们的对端在后
    面设置。

    连接veth到Namespace:

        ip link set veth1 netns ns1
        ip link set veth2 netns ns2
    
    设置IP地址：

        ip -n ns1 address add 10.120.0.11/24 dev veth1
        ip -n ns2 address add 10.120.0.12/24 dev veth2

    启用veth设备：

        ip -n ns1 link set veth1 up
        ip -n ns2 link set veth2 up

1. **连接veth设备的另一端到Linux Bridge并启用**

    将`br1-veth1`和`br1-veth2`连接到Linux Bridge `br1`上，并启用。连接在Bridge上的设备
    是不需要设置IP地址的，直接启用后就可以使用了。

    连接veth到Bridge:

        ip link set br1-veth1 master br1
        ip link set br1-veth2 master br1

    上面命令中的`master`参数后面紧跟另一个设备的名字，这个设备将作为当前设备的master设备。在
    这里就意味着将`br1-veth1`和`br1-veth2`连接到`br1`上。

    此时，除了使用上文中的方便来查看设备的以外，还可以通过`master`参数来查看连接到一个Bridge
    上的所有设备：

        ip link show master br1
        ip address show master br1
    
    接下来，启用Bridge上连接的VETH设备：

        ip link set br1-veth1 up
        ip link set br1-veth2 up

1. **验证Namespace之间的连通性**

        ip netns exec ns1 ping -c 5 10.120.0.12
        ip netns exec ns2 ping -c 5 10.120.0.11

## 清理实验资源

1. 清理Namespace和VETH

        ip -n ns1 link dev veth1
        ip -n ns2 link dev vthe2
        ip netns del ns1
        ip netns del ns2

    Namespace和VETH资源的清理，和上一节的清理方式相同，这里不再详细说明。

    如果需要只将VETH从一个Bridge上断开连接，可以使用如下命令：

        ip link set br1-veth1 nomaster

    `nomaster`参数就表示将`br1-veth1`设备的master设备清空，也就意味着`br1-veth1`从`br1`
    上解绑了。

    如果需要将一个VETH设备从一个Bridge连接到另一个，比如将原本连接在`br1`上的`br1-veth1`
    连接到`br2`上，可以使用以下命令：

        ip link set br1-veth1 master br2

1. 清理Linux Bridge

    删除Bridge的方法和删除其他Link虚拟连接的方式相同：

        ip link del br1

# 同一Linux Bridge连接多个网段

按照上一节的方法连接到同一个Linux Bridge下的Namespace，其网络设备是可以属于不同网段的。其网
段是根据设备的地址和掩码来确认的。比如`10.120.1.11/24`和`10.120.1.12/24`同属于网段
`10.120.1.0/24`网段。而`10.120.2.11/24`则属于另一个网段`10.120.2.0/24`。

连在同一个Bridge下的、属于不同网段的Namespace网络设备，默认情况下相互之间也是不能通信的。比如
下图中

![同一Linux Bridge连接多个网段]({{site.url}}/assets/img/namespace-interconnecting-with-linux-bridge/linux_bridge_multi_net.png)

Namespace `ns11`与`ns12`之间，`ns21`与`ns22`之间是互通的，但其他的连接都是不通的。比如
`ns11`无法与`ns21`或者`ns22`互通。

1. **创建Namespace**

        ip netns add ns11
        ip netns add ns12
        ip netns add ns21
        ip netns add ns22

1. **创建Linux Bridge并启用**

        ip link add br1 type bridge
        ip link set br1 up

1. **创建VETH对**

        ip link add veth11 type veth peer name br1-veth11
        ip link add veth12 type veth peer name br1-veth12
        ip link add veth21 type veth peer name br1-veth21
        ip link add veth22 type veth peer name br1-veth22

1. **连接VETH到Namespace、设置地址并启用**

        ip link set veth11 netns ns11
        ip link set veth12 netns ns12
        ip link set veth21 netns ns21
        ip link set veth22 netns ns22
        ip -n ns11 address add 10.120.1.11/24 dev veth11
        ip -n ns12 address add 10.120.1.12/24 dev veth12
        ip -n ns21 address add 10.120.2.21/24 dev veth21
        ip -n ns22 address add 10.120.2.22/24 dev veth22
        ip -n ns11 link set veth11 up
        ip -n ns12 link set veth12 up
        ip -n ns21 link set veth21 up
        ip -n ns22 link set veth22 up

1. **连接VETH到Linux Bridge并启用**

        ip link set br1-veth11 master br1
        ip link set br1-veth12 master br1
        ip link set br1-veth21 master br1
        ip link set br1-veth22 master br1
        ip link set br1-veth11 up
        ip link set br1-veth12 up
        ip link set br1-veth21 up
        ip link set br1-veth22 up

1. **验证Namespace间的网络连通性**

    同一个网段下的Namespace是可以互通的：

        ip netns exec ns11 ping -c 5 10.120.1.12
        ip netns exec ns12 ping -c 5 10.120.1.11
        ip netns exec ns21 ping -c 5 10.120.2.22
        ip netns exec ns22 ping -c 5 10.120.2.21

    而不同网段之间是不通的，比如：

        ip netns exec ns11 ping -c 5 10.120.2.21
        ip netns exec ns21 ping -c 5 10.120.1.11

## 多网段之间打通

Linux Bridge是工作在2层，根据MAC地址来对信息进行操作，所以不同网段之间的隔离并不是由于Linux
Bridge导致的。

对一个Namespace，比如`ns11`执行以下命令：

    ip -n ns11 route show

这条命令会显示所有的路由规则。这里我们可以得到如下输出：

    10.120.1.0/24 dev veth11  proto kernel  scope link  src 10.120.1.11

我们感兴趣的部分是`10.120.1.0/24 dev veth11`。其中`10.120.1.0/24`部分，表示这条规则对于
地址属于这个网段的访问目标生效。`dev veth11`表示符合这条规则的数据，会从网络设备`veth11`上
发送。

所以，这条规则组合起来的意思就是，对于目标地址是`10.120.1.0/24`网段的数据，会通过网络设备
`veth11`发送。所以，当我们从Namespace `ns11`上执行ping Namespace `ns12`的地址
`10.120.1.12`，ICMP数据包就会根据这条规则，从`veth11`发送出去，通过Linux Bridge `br1`，
最终到达`ns12`。

然而，如果从`ns11`上ping Namespace `ns21`的地址`10.120.2.21`，是没有可以匹配的路由规则
的，这时，Linux系统就会将这些数据包丢弃，所以最终没有数据会从`ns11`发送出来，对外表现为网络不
通。

对于这种情况，除了查看所有的路由规则进行分析外，我们可以通过`ip route show to match`命令，
来查看目标地址属于特定网段网络的数据，会应用哪些路由规则。比如：

    ip -n ns11 route show to match 10.120.1.0/24

这条命令会有如下输出：

    10.120.1.0/24 dev veth11  proto kernel  scope link  src 10.120.1.11

和我们上文中的分析相同，`10.120.1.0/24 dev veth11`这条规则会被应用。

而命令

    ip -n ns11 route show to match 10.120.2.0/24

的输出是空的，说明到`10.120.2.0/24`网段没有可用的路由规则。

为了连通不同网段下的Namespace，需要修改路由规则：

    ip -n ns11 route add default dev veth11
    ip -n ns12 route add default dev veth12
    ip -n ns21 route add default dev veth21
    ip -n ns22 route add default dev veth22

`add`参数表示执行的是路由添加操作，后面是新的路由规则。`default`表示没有其他规则可用时，默认
匹配使用这条规则。`dev veth11`表示匹配新规则的数据通过设备`veth11`发送。所以新规则的意思就是
在没有其他规则可用的情况下，默认使用网络设备`veth11`发送数据。由于绝大部分的网络通信都需要通信
双方都能够向对方发送数据，所以这里需要在所有的Namespace里添加默认的路由规则。

这时，我们再检测不同网段间的连通性

    ip netns exec ns11 ping -c 5 10.120.2.21
    ip netns exec ns21 ping -c 5 10.120.1.11

就可以发现，不同网段间的Namespace可以互通了。

当然，我们在`ns11`和`ns12`上也可以显式指定对于`10.120.2.0/24`网段的路由规则：

    ip -n ns11 route add 10.120.2.0/24 dev veth11
    ip -n ns12 route add 10.120.2.0/24 dev veth12

在`10.120.2.0/24`网段的Namespace的路由规则正确的情况下，就算没有默认路由规则，这时它们之间
也是可以互通的。

这种方式的限制就是每次有新的网段需要连通时，都需要在所有的相关Namespace添加路由规则。

## 清理实验资源

在网络设备被删除时，和它相关的路由规则也会同时被自动删除，所以一般不需要手工删除。如果需要显式清
理路由规则时，可以使用如下命令：

    ip -n ns11 route del 10.120.2.0/24 dev veth11
    ip -n ns11 route del default dev veth11

形式类似添加路由规则的命令。

实验的其他资源清理方式和之前是相同的：

    ip -n ns11 link del veth11
    ip -n ns12 link del veth12
    ip -n ns21 link del veth21
    ip -n ns22 link del veth22
    ip link del br1
    ip netns del ns11
    ip netns del ns12
    ip netns del ns21
    ip netns del ns22

# 模拟网关

前一节的例子中，通过修改默认路由，让Namespace默认将所有的数据都发送到Linux Bridge上，来实现
不同网段的Namespace互通。这种方式下，无法通过集中的方式来对网段进行隔离。比如，如果我们只希望
`10.120.1.0/24`和`10.120.2.0/24`互通，而与`10.120.3.0/24`不通，必须在所有的Namespace
上做修改。

为了解决这个问题，我们可以引入模拟网关的Namespace。结构如下图：

![使用Namespace模拟网关]({{site.url}}/assets/img/namespace-interconnecting-with-linux-bridge/linux_bridge_with_router.png)

上图中，Namespace `nsgw`上的VETH设备用来作为`10.120.1.0/24`和`10.120.2.0/24`的网关，
然后将各个Namespace的默认路由设置为自己所在网络的网关。

1. **创建Namespace、VETH和Bridge**

    这一步创建和上一节中相同的设备，相关的配置也一样。为接下来创建和配置模拟网关作准备：

        ip netns add ns11
        ip netns add ns12
        ip netns add ns21
        ip netns add ns22
        ip link add br1 type bridge
        ip link set br1 up
        ip link add veth11 type veth peer name br1-veth11
        ip link add veth12 type veth peer name br1-veth12
        ip link add veth21 type veth peer name br1-veth21
        ip link add veth22 type veth peer name br1-veth22
        ip link set veth11 netns ns11
        ip link set veth12 netns ns12
        ip link set veth21 netns ns21
        ip link set veth22 netns ns22
        ip -n ns11 address add 10.120.1.11/24 dev veth11
        ip -n ns12 address add 10.120.1.12/24 dev veth12
        ip -n ns21 address add 10.120.2.21/24 dev veth21
        ip -n ns22 address add 10.120.2.22/24 dev veth22
        ip -n ns11 link set veth11 up
        ip -n ns12 link set veth12 up
        ip -n ns21 link set veth21 up
        ip -n ns22 link set veth22 up
        ip link set br1-veth11 master br1
        ip link set br1-veth12 master br1
        ip link set br1-veth21 master br1
        ip link set br1-veth22 master br1
        ip link set br1-veth11 up
        ip link set br1-veth12 up
        ip link set br1-veth21 up
        ip link set br1-veth22 up

1. **创建模拟网关Namespace和VETH设备**

        ip netns add nsgw
        ip link add vethgw1 type veth peer name br1-vethgw1
        ip link add vethgw2 type veth peer name br1-vethgw2
        ip link set br1-vethgw1 master br1
        ip link set br1-vethgw2 master br1
        ip link set br1-vethgw1 up
        ip link set br1-vethgw2 up
        ip link set vethgw1 netns nsgw
        ip link set vethgw2 netns nsgw
        ip -n nsgw address add 10.120.1.1/24 dev vethgw1
        ip -n nsgw address add 10.120.2.1/24 dev vethgw2
        ip -n nsgw link set vethgw1 up
        ip -n nsgw link set vethgw2 up

    Namespace `nsgw`就有了两个VETH设备来充当网关，这两个VETH设备也都连接到了Bridge上。这
    时，各个Namespace都可以和所在网络的“网关”连通了：

        ip netns exec ns11 ping -c 5 10.120.1.1
        ip netns exec ns12 ping -c 5 10.120.1.1
        ip netns exec ns21 ping -c 5 10.120.2.1
        ip netns exec ns22 ping -c 5 10.120.2.1

1. **修改Namespace的默认路由规则**

    为了让发往其他网段的数据能够首先到达网关，我们需要在所有的Namespace添加默认路由规则：

        ip -n ns11 route add default via 10.120.1.1
        ip -n ns12 route add default via 10.120.1.1
        ip -n ns21 route add default via 10.120.2.1
        ip -n ns22 route add default via 10.120.2.1

    现在，所有的Namespace都已经可以和对方网段的网关连通了：

        ip netns exec ns11 ping -c 5 10.120.2.1
        ip netns exec ns12 ping -c 5 10.120.2.1
        ip netns exec ns21 ping -c 5 10.120.1.1
        ip netns exec ns22 ping -c 5 10.120.1.1
    
    然而，此时不同网段的Namespace之间仍然是不通的。

1. **在网关Namespace上开启网络转发**

    现在所有的Namespce的数据默认都会发送到网关`nsgw`上，然而`nsgw`在收到一个不属于自己VETH
    设备地址的数据时，认为不是发送给自己的，然后丢弃了，所以此时不同网段时的Namespace仍然不能
    互通。

    这时，我们需要开启`nsgw`上的网络转发功能，让它在收到不属于自己设备地址的数据时，会根据目的
    地址进行转发。

    首先，我们可以通过以下命令查看`nsgw`与网络转发相关的内核设置：

        ip netns exec nsgw sysctl net.ipv4.ip_forward 

    命令会有如下返回值：

        net.ipv4.ip_forward = 0
 
    `0`表示这IPv4的IP转发是关闭的。接下来执行以下命令来开启这个功能：

        ip netns exec nsgw sysctl -w net.ipv4.ip_forward=1

    这里的`sysctl`是一个Linux内核参数管理工具。`net.ipv4.ip_forward`则是一个内核参数的名
    字。可以通过`sysctl -all`命令来查看所有的内核参数，也可以通过
    `sysctl -a -r "<pattern>"`来搜索名字符合指定pattern的参数。 `-w`参数则会根据后面的参
    数修改参数值。

    现在我们就可以从一个网段的Namespace向不同网段的Namespace进行通信了：

        ip netns exec ns11 ping -c 5 10.120.2.21
        ip netns exec ns21 ping -c 5 10.120.1.11

使用这种方案，“网关”在不同Namespace下的网络之间，是不能互通。但是，由于Linux Bridge本身工作
在2层，而且不会对其上的网络进行任何隔离，所以仍然可以修改对个别Namespace的路由规则来绕过这种访
问限制。另外，由于同样的原因，同一个Linux Bridge上的所有的设备的IP地址都必须是唯一的。

## 清理实验资源

实验的其他资源清理方式和之前是相同的：

    ip -n ns11 link del veth11
    ip -n ns12 link del veth12
    ip -n ns21 link del veth21
    ip -n ns22 link del veth22
    ip -n nsgw link del vethgw1
    ip -n nsgw link del vethgw2
    ip link del br1
    ip netns del ns11
    ip netns del ns12
    ip netns del ns21
    ip netns del ns22
    ip netns del nsgw

# 小结

本文介绍了在Linux上使用虚拟网络设备Linux Bridge和VETH来搭建虚拟网络的一些基本方式，以及由于
Linux Bridge自身原理产生的一些限制。同时，也简单介绍了路由规则对于网络通信的影响。最后，为了
模拟一个基本的网关，还接触到了Linux中关于网络的内核参数。

Linux Bridge相关的概念和操作可以参考以下一些文档：

- [Bridge setup on Linux Foundation](https://wiki.linuxfoundation.org/networking/bridge)
- [Bridging on Fedora Proejct](http://fedoraproject.org/wiki/Networking/Bridging)

对于vTAP、VETH设备，以及它们和Linux Bridge之间的关系，可以参考以下一些文档：

- [Linux 上的基础网络设备详解](https://www.ibm.com/developerworks/cn/linux/1310_xiawc_networkdevice/)
- [Virtual Ethernet device](https://openvz.org/Virtual_Ethernet_device)

这两篇文章对于本文有非常大的启发：

- [Linux Switching – Interconnecting Namespaces](http://www.opencloudblog.com/?p=66)
- [Fun with veth devices, Linux virtual bridges, KVM, VMware – attach the host and connect bridges via veth](http://linux-blog.anracom.com/2016/02/02/fun-with-veth-devices-linux-virtual-bridges-kvm-vmware-attach-the-host-and-connect-bridges-via-veth/)

本文中，主要使用iproute2工具来对网络设备进行操作。关于这个工具，一个比较完整的文档是：

[Baturin's iproute2 Doc](http://baturin.org/docs/iproute2/)

`brctl`是一个用来专门对Linux Bridge进行管理和操作的工具。它的使用非常广泛，文档众多，使用方法
和iproute2的相关命令很类似。本文不再展示具体例子，以及文档链接。
