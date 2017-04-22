---
layout: post
title:  "使用KVM创建虚拟机"
date:   2017-04-20 22:55:36 +0800
categories: KVM
---

# KVM简介

TBD

## 创建无网络的虚拟机

### 使用条件

使用KVM需要首先确认CPU是否支持vmx或者svm特性。在Linux系统下可以使用以下命令来确认：

    # grep -E "vmx|svm" /proc/cpuinfo

如果此命令的输出不为空，如多行如下输出：

    flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm cqm rdseed adx smap xsaveopt cqm_llc cqm_occup_llc

说明CPU是支持KVM必需的虚拟化特性的。

如果输出为空，则说明CPU不支持KVM的运行。

### 包安装

在RedHat或者CentOS下，使用yum安装必需的包：

    # yum install -y qemu-kvm libvirt virt-install

其中：

*   qemu-kvm是QEMU和KVM的组合，分别用来进行硬件模拟和系统虚拟化。
*   libvirt是一套标准的虚拟机系统的管理接口
*   virt-install是用来安装虚拟器的工具

包安装完成后，需要激活并启动libvirtd服务：

    systemctl enable libvirtd && systemctl start libvirtd

接下来需要检查必要的内核模块：

    lsmod | grep "kvm"

正常情况下，输出应当有kvm和kvm_intel或者kvm_amd，如:

    kvm_intel             162153  0
    kvm                   525259  1 kvm_intel

如果内核模块没有加载，需要手动加载：

    # modprobe kvm

* 对于Intel平台，还需要执行 
    
        # modprobe kvm-intel

* 对于AMD平台

        # modprobe kvm-amd

### 导入现有磁盘镜像

使用`virt-install`可以导入一个已经安装配置好的系统的镜像文件。导入完成后，这个镜像文件还会作
为虚拟机系统运行时的系统分区，用于继续保存系统的文件。

接下来的例子中，会使用CirrOS镜像文件。CirrOS是一个精简的Linux内核系统，经常用在云平台的测试
中。CirrOS镜像可以在
[http://download.cirros-cloud.net/](http://download.cirros-cloud.net/)
下载到。比如
[cirros-0.3.5-i386-disk.img](http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-i386-disk.img)
。

我们可以使用`qemu-img`工具来查看和操作磁盘镜像文件。比如，使用以下命令来查看当前目录下的
cirros-0.3.5-i386-disk.img 镜像文件信息：

    # qemu-img info cirros-0.3.5-i386-disk.img

    image: cirros-0.3.5-i386-disk.img
    file format: qcow2
    virtual size: 39M (41126400 bytes)
    disk size: 12M
    cluster_size: 65536
    Format specific information:
        compat: 0.10

返回值中的file format字段是指磁盘镜像文件的格式，这里CirrOS的镜像格式是qcow2，也即QEMU的一
种 copy-on-write 格式。对于镜像格式，这里不再展开。

下载好磁盘镜像文件后，就可以进行虚拟机的安装了。

一般来说，libvirt维护的虚拟机的磁盘镜像都保存在`/var/lib/libvirt/images/`目录下，所以这里
我们首先将下载的镜像文件拷贝到这个目录下：

    # cp cirros-0.3.5-i386-disk.img /var/lib/libvirt/images/cirros-vm.img

然后，就可以通过导入磁盘镜像的方式来创建虚拟机了：

    # virt-install --name cirros-vm \
            --ram 500 \
            --disk path=/var/lib/libvirt/images/cirros-vm.img \
            --accelerate \
            --vnc \
            --import \
            --noautoconsole

这里，各个参数的意义如下：

-   `name` 虚拟机的名字。同一个宿主机上的虚拟机的名字必须是唯一的。
-   `ram` 内存大小，单位为MB。这里，虚拟机的内存为500MB。
-   `disk` 指定用于虚拟机系统磁盘。`path=/var/lib/libvirt/images/cirros-vm.img`表示，
    使用在路径为`/var/lib/libvirt/images/cirros-vm.img`的镜像。
-   `accelerate` 激活KVM内核加速。
-   `vnc` 激活虚拟机的VNC访问。
-   `import` 表示当前是通过导入已有磁盘镜像上的系统来创建虚拟机，不需要指定系统安装源介质，比
    系统光盘镜像。
-   `noautoconsole` 表示虚拟机的安装命令成功发出后，会结束当前命令，而不会自动连接到虚拟机
    控制台。

执行完`virt-install`命令后，可以使用`virsh`命令对虚拟机进行管理操作。比如查看当前宿主机上的
所有虚拟机：

    # virsh list --all
     Id    Name                           State
    ----------------------------------------------------
    6     cirros-vm                      running
    -     cirros-1                       shut off

参数`--all`表示显示所有的虚拟机，包括已关机的。如果不指定此参数，默认只显示运行中的虚拟机。

上例中，宿主机上有两个虚拟机，运行中的cirros-vm和关机的cirros-1。只有运行中的虚拟机会显示Id。

由于现在还没有配置好虚拟的网络和SSH服务，可以通`virsh console`来连接到虚拟机：

    # virsh console cirros-vm
    Connected to domain cirros-vm
    Escape character is ^]

    login as 'cirros' user. default password: 'cubswin:)'. use 'sudo' for root.
    cirros login:

以上输出中的第一行表示虚拟机的控制台已经成功连接上。第二行则是提示可以使用快捷键`ctrl+]`来退出
控制台连接。

很多时候，在连接上虚拟机控制台后，就算虚拟机操作系统已经可以访问，也不会显示登陆或者对话提示，这
时可以输入回车来让系统再次显示登录或者控制台对话提示。比如，上例输出的后两行即CirrOS的登录提示。
注意，如上面的登录提示所述，CirrOS的默认登录账号和密码是"cirros"和"cubswin:)"。

### 使用光盘镜像安装新系统

除了导入一个已有的磁盘镜像，还可以通过系统安装光盘镜像来安装一个新的虚拟机。

首先，我们需要准备系统安装光盘的镜像文件。比如，可以在
[https://www.centos.org/download/](https://www.centos.org/download/)
找到所需的CentOS安装镜像。接下来的例子中，会使用
[CentOS-7-x86_64-Minimal-1611.iso](http://mirrors.sohu.com/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-1611.iso)。
KVM会使用qemu账号来运行虚拟机的模拟进程，所以需要将镜像文件放到qemu账号有权限访问的目录下，比
如：

    # mv CentOS-7-x86_64-Minimal-1611.iso /tmp/

然后就可以执行以下命令开始虚拟机安装了：

    # virt-install --name centos7 \
        --ram=1024 \
        --vcpus=2 \
        --disk path=/var/lib/libvirt/images/centos7.img,size=10,bus=virtio,format=qcow2 \
        --accelerate \
        --vnc --vncport=6001 --vnclisten=0.0.0.0 \
        --noautoconsole \
        --cdrom=/tmp/CentOS-7-x86_64-Minimal-1611.iso

这个命令比之前多了一些参数：

- `vcpus` 虚拟机的虚拟CPU内核数量。
- `disk` 参数中，除了`path`以外，还多了`size`, `bus`和 `format`部分。`size`是虚拟机系统
    磁盘大小，单位为"GB"。`bus`是磁盘驱动类型，一般为"virtio“。`format`是指磁盘镜像文件的
    格式，这里同样是"qcow2"。在这个例子中，指定的磁盘镜像文件并不存在，KVM会根据参数自动创建
    一个新的文件。
- `vnc` 参数后面多了两个与VNC相关的参数，`vncport`和`vnclisten`。`vncport`指定此虚拟机的
    VNC服务在当前宿主机上的监听端口。`vnclisten`这里指定的"0.0.0.0"则指虚拟机的VNC服务在宿
    主机上监听所有IP地址。后面会详细讲解如何根据这两个参数来连接虚拟机的VNC。
- `cdrom` 指定操作系统安装光盘镜像文件的地址。

由于CentOS默认情况下不会开启TTY，所以此时还不能通过`virsh console`命令来连接虚拟机，而需要
使用VNC客户端。接下来会用Chrome浏览器的VNC Viewer插件来演示。VNC Viewer插件可以在Chrome浏
览器的插件市场里找到（需要翻墙）。

根据上例中的VNC相关参数，可以知道新虚拟机的VNC服务是在宿主机的所有IP地址上监听6001端口。如所
使用的宿主机IP地址为10.0.12.26，那么我们在VNC Viewer上指定VNC指定地址就是10.0.12.16:6001
, 如下图所示：

 ![VNC Viewer连接]({{ site.url }}/assets/img/vnc_connection.png)

由于没有使用安全链接，在上面的登录窗口点击“Connect”后，如果虚拟机的VNC可以正常访问，会有连接
未加密的警告提示：

![VNC View连接加密警告]({{ site.url }}/assets/img/vnc_connection_warning.png)

忽略此警告，点击警告窗口上的"Connect"后，就可以看到CentOS的安装窗口了：

![VNC Viewer安装CentOS窗口]({{ site.url }}/assets/img/vnc_centos_install.png)

接下来就可以安装一般安装CentOS的方式进行后续的安装操作了。

系统安装最后安装程序会尝试自动重启，此时有可能虚拟机关机后不会自动启动，需要我们手动启动。

首先，我们可以通过`virsh list --all`命令查看虚拟机状态，如果发现的确虚拟机状态为`shut down`
就可以使用`virsh start`命令来手动启动：

    # virsh start centos7

命令中的参数`centos7`是我们安装虚拟机时指定的虚拟机名字。

默认情况下，CentOS是不开启ttyS0的，我们需要手动配置和启用，否则无法通过`virsh console`命令
来访问。

首先，修改配置文件`/etc/sysconfig/grub`，在`GRUB_CMD_LINELINUX`中添加
`console=ttyS0`, 如：

{% highlight shell linenos %}
GRUB_TIMEOUT=5
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT="console"
GRUB_CMDLINE_LINUX="rd.lvm.lv=centos/root rd.lvm.lv=centos/swap crashkernel=auto rhgb quiet console=ttyS0"
GRUB_DISABLE_RECOVERY="true"
{% endhighlight %}

中的第5行最后部分。

接下来执行以下命令来设置并启用ttyS0：

    # stty -F /dev/ttyS0 speed 9600
    # grub2-mkconfig -o /boot/grub2/grub.cfg
    # systemctl start serial-getty@ttyS0

这样，就可以通过`virsh console`来连接虚拟机了。