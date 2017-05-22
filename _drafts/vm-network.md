http://www.opencloudblog.com/?p=66 Linux Switching – Interconnecting Namespaces
https://www.ibm.com/support/knowledgecenter/linuxonibm/liaat/liaatbestpractices_pdf.pdf Best practices for KVM
https://en.wikipedia.org/wiki/TUN/TAP
https://en.wikipedia.org/wiki/Network_tap
http://blog.csdn.net/tantexian/article/details/45395075 openstack neutron(tap、qvb、qvo详解)（转）
http://www.linux-kvm.org/page/Networking Configuring Guest Networking
http://backreference.org/2010/03/26/tuntap-interface-tutorial/ Tun/Tap interface tutorial
http://linux.it.net.cn/CentOS/course/2016/1115/24865.html CentOS下使用TUN/TAP虚拟网卡的基本教程
https://wiki.linuxfoundation.org/networking/bridge linux bridge
https://wiki.centos.org/HowTos/KVM KVM and CentOS-6
http://libvirt.org/sources/virshcmdref/html/sect-net-create.html 


veth pair

ovs

install openvswitch 

install build prerequisities:
    `yum install gcc rpmbuild openssl-devel `

download openvswitch source code tarball
    `wget http://openvswitch.org/releases/openvswitch-2.5.2.tar.gz`

    http://openvswitch.org/download/

setup build directory
    `
    mkdir $HOME/rpmbuild/SOURCES
    mv openvswitch-2.5.2.tar.gz $HOME/rpmbuild/SOURCES
    cd $HOME/rpmbuild/SOURCES
    tar xvf openvswitch-2.5.2.tar.gz
    cd openvswitch-2.5.2
    rpmbuild -bb rhel/openvswitch.spec
    `

install openvswitch rpm
    `rpm -i $HOME/rpmbuild/RPMS/x86_64/openvswitch-2.5.2-1.x86_64.rpm`
    
start openvswitch service
    `systemctl enable openvswitch && systemctl start openvswitch`




ip netns exec nsgw sysctl net.ipv4.conf.vethgw2.forwarding=1



# 多个Linux Bridge之间互联

    ip link add br1 type bridge 
    ip link add br2 type bridge 
    ip link add br3 type bridge 
    ip link set br1 up
    ip link set br2 up
    ip link set br3 up

    ip link add veth-br1-br2 type veth peer name veth-br2-br1
    ip link add veth-br2-br3 type veth peer name veth-br3-br2
    ip link set veth-br1-br2 master br1
    ip link set veth-br2-br1 master br2
    ip link set veth-br2-br3 master br2
    ip link set veth-br3-br2 master br3
    ip link set veth-br1-br2 up
    ip link set veth-br2-br1 up
    ip link set veth-br2-br3 up
    ip link set veth-br3-br2 up

    ip netns add ns1
    ip netns add ns2

    ip link add br1-veth1 type veth peer name veth1
    ip link add br3-veth2 type veth peer name veth2
    ip link set br1-veth1 master br1
    ip link set br3-veth2 master br2
    ip link set br1-veth1 up
    ip link set br3-veth2 up

    ip link set veth1 netns ns1
    ip link set veth2 netns ns2

    ip -n ns1 address add 10.120.1.11/24 dev veth1
    ip -n ns2 address add 10.120.1.12/24 dev veth2

    ip -n ns1 link set veth1 up
    ip -n ns2 link set veth2 up

# VLan with bridge

    ip link add br1 type bridge
    ip link set br1 up

    ip netns add ns11
    ip netns add ns12
    ip netns add ns21
    ip netns add ns31

    ip link add veth11 type veth peer name br1-veth11
    ip link add veth12 type veth peer name br1-veth12
    ip link add veth21 type veth peer name br1-veth21
    ip link add veth31 type veth peer name br1-veth31

    ip link set veth11 netns ns11
    ip link set veth12 netns ns12
    ip link set veth21 netns ns21
    ip link set veth31 netns ns31

    ip -n ns11 address add 10.120.1.11/24 dev veth11
    ip -n ns12 address add 10.120.1.12/24 dev veth12
    ip -n ns21 address add 10.120.2.21/24 dev veth21
    ip -n ns31 address add 10.120.3.31/24 dev veth31

    ip -n ns11 link set veth11 up
    ip -n ns12 link set veth12 up
    ip -n ns21 link set veth21 up
    ip -n ns31 link set veth31 up

    ip link add name br1-veth11.100 link br1-veth11 type vlan id 100
    ip link add name br1-veth12.100 link br1-veth12 type vlan id 100
    ip link add name br1-veth21.100 link br1-veth21 type vlan id 100
    ip link add name br1-veth31.300 link br1-veth31 type vlan id 300

    ip link set br1-veth11.100 master br1
    ip link set br1-veth12.100 master br1
    ip link set br1-veth21.100 master br1
    ip link set br1-veth31.300 master br1

    ip link set br1-veth11 up
    ip link set br1-veth12 up
    ip link set br1-veth21 up
    ip link set br1-veth31 up


    ip link set br1-veth11.100 up
    ip link set br1-veth12.100 up
    ip link set br1-veth21.100 up
    ip link set br1-veth31.300 up



## vlan tag within namespace

    ip link add br1 type bridge
    ip link set br1 up

    ip netns add ns11
    ip netns add ns12

    ip netns add ns13

    ip netns add ns21

    ip link add veth11 type veth peer name br1-veth11
    ip link add veth12 type veth peer name br1-veth12

    ip link add veth13 type veth peer name br1-veth13

    ip link add veth21 type veth peer name br1-veth21

    ip link set br1-veth11 master br1
    ip link set br1-veth12 master br1
    ip link set br1-veth11 up
    ip link set br1-veth12 up

    ip link set br1-veth13 master br1
    ip link set br1-veth13 up

    ip link set br1-veth21 master br1
    ip link set br1-veth21 up

    ip link set veth11 netns ns11
    ip link set veth12 netns ns12

    ip link set veth13 netns ns13

    ip link set veth21 netns ns21

    ip -n ns11 link add name veth11.100 link veth11 type vlan id 100
    ip -n ns12 link add name veth12.100 link veth12 type vlan id 100

    ip -n ns13 link add name veth13.200 link veth13 type vlan id 200

    ip -n ns21 link add name veth21.200 link veth21 type vlan id 200

    ip -n ns11 address add 10.120.1.11/24 dev veth11.100
    ip -n ns12 address add 10.120.1.12/24 dev veth12.100

    ip -n ns13 address add 10.120.1.13/24 dev veth13.200

    ip -n ns21 address add 10.120.2.21/24 dev veth21.200

    ip -n ns11 link set veth11 up
    ip -n ns11 link set veth11.100 up
    ip -n ns12 link set veth12 up
    ip -n ns12 link set veth12.100 up

    ip -n ns13 link set veth13 up
    ip -n ns13 link set veth13.200 up

    ip -n ns21 link set veth21 up
    ip -n ns21 link set veth21.200 up

    ip -n ns13 route add 10.120.2.0/24 dev veth13.200

    ip -n ns21 route add 10.120.1.0/24 dev veth21.200

# create vlan on bridge

    ip link add br1 type bridge
    ip link set br1 up

    ip link add br1.100 link br1 type vlan id 100
    ip link add br1.200 link br1 type vlan id 200

    ip link set br1.100 up
    ip link set br1.200 up

    ip link add veth11 type veth peer name veth11-br1.100
    ip link add veth12 type veth peer name veth12-br1.100

    ip link set veth11-br1.100 master br1.100

# create vlan link for namespace

    ip link add br1 type bridge
    ip link set br1 up

    ip link add veth11 type veth peer name br1-veth11
    ip link add veth12 type veth peer name br1-veth12

    ip link add veth11.100 link veth11 type vlan id 100
    ip link add veth12.100 link veth12 type vlan id 100
    ip link set veth11 up
    ip link set veth12 up

    ip link set br1-veth11 master br1
    ip link set br1-veth12 master br1
    ip link set br1-veth11 up
    ip link set br1-veth12 up

    ip netns add ns11
    ip netns add ns12

    ip link set veth11.100 netns ns11
    ip link set veth12.100 netns ns12

    ip -n ns11 address add 10.120.1.11/24 dev veth11.100
    ip -n ns12 address add 10.120.1.12/24 dev veth12.100
    ip -n ns11 link set veth11.100 up
    ip -n ns12 link set veth12.100 up