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