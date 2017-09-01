---
layout: post
title:  "在Docker中运行Jupyter Notebook"
date:   2017-04-20 22:55:36 +0800
categories: Docker Jupyter 
---

今天尝试了在Docker中运行Jupyter Notebook。这个过程中遇到了一些问题，在这里作一下记录。

# 运行环境

宿主机：macOS 10.12.6
Docker： 17.06.1-ce, build 874a737
Python: 2.7.12
Jupyter: 4.3.0

# 基本安装

1. 启动Container

        `docker -p 8888:8888 -it ubuntu:16.04 /bin/bash`

    jupyter notebook server默认使用8888端口，所以需要将container的8888端口暴露出来。

1. 在Container中安装Python和PyPi，然后根据官方文档[Installing Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/install.html)
安装Jupyter

# 启动Jupyter Notebook Server

`jupyter notebook --no-browser --ip=0.0.0.0 --allow-root`

其中参数`--ip=0.0.0.0`用来指定server需要监听所有的IP地址。如果不指定，Jupyter Notebook
server会监听`localhost`。此时会发生以下错误：

    Traceback (most recent call last):
      File "/usr/local/bin/jupyter-notebook", line 11, in <module>
        sys.exit(main())
      File "/usr/local/lib/python2.7/dist-packages/jupyter_core/application.py", line 267, in launch_instance
        return super(JupyterApp, cls).launch_instance(argv=argv, **kwargs)
      File "/usr/local/lib/python2.7/dist-packages/traitlets/config/application.py", line 657, in launch_instance
        app.initialize(argv)
      File "<decorator-gen-7>", line 2, in initialize
      File "/usr/local/lib/python2.7/dist-packages/traitlets/config/application.py", line 87, in catch_config_error
        return method(app, *args, **kwargs)
      File "/usr/local/lib/python2.7/dist-packages/notebook/notebookapp.py", line 1296, in initialize
        self.init_webapp()
      File "/usr/local/lib/python2.7/dist-packages/notebook/notebookapp.py", line 1120, in init_webapp
        self.http_server.listen(port, self.ip)
      File "/usr/local/lib/python2.7/dist-packages/tornado/tcpserver.py", line 142, in listen
        sockets = bind_sockets(port, address=address)
      File "/usr/local/lib/python2.7/dist-packages/tornado/netutil.py", line 197, in bind_sockets
        sock.bind(sockaddr)
      File "/usr/lib/python2.7/socket.py", line 228, in meth
        return getattr(self._sock,name)(*args)
    socket.error: [Errno 99] Cannot assign requested address

指定监听IP为`127.0.0.1`，server也可以正常启动。但此时，server只能接受本地访问，从宿主机上不
能访问。为了从宿主机能够访问，这里设置为`0.0.0.0`来监听所有的IP。当然，设置为Container的IP
也是可以的。

由于我们是要从宿主机，而不是Container内部访问Notebook Server，所以加上`--no-browser`参数
来阻止Server启动后自动打开浏览器。

因为是使用的`root`用户启动，所以加上`--allow-root`来关闭安全检查。

如果没有其他错误信息，就可以在宿主机上通过浏览器来访问了。`