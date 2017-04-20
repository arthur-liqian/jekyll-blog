# 使用KVM创建虚拟机

## KVM简介

TBD

### 创建无网络的虚拟机

#### 使用条件

使用KVM需要首先确认CPU是否支持vmx或者svm特性。在Linux系统下可以使用以下命令来确认：

    # grep -E "vmx|svm" /proc/cpuinfo

如果此命令的输出不为空，如多行如下输出：

    flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm cqm rdseed adx smap xsaveopt cqm_llc cqm_occup_llc

说明CPU是支持KVM必需的虚拟化特性的。

如果输出为空，则说明CPU不支持KVM的运行。

#### 包安装

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

#### 导入现有系统镜像

使用`virt-install`可以导入一个已经安装配置好的系统的镜像文件。导入完成后，这个镜像文件还会作为虚拟机系统运行时的系
统分区，用于继续保存系统的文件。

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
