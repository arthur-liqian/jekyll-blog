# Installation

Environment CentOS 7.2

## Installation with `yum`

    yum intall -y rabbitmq-server

## Start RabbitMQ Server

- setup RabbitMQ server service

    chkconfig rabbitmq-server on

- startup RabbitMQ server service

    systemctl start rabbitmq-server

NOTE: When RabbitMQ server starts up, it will try to access to the local server
via host name. Please make sure the host name can be translated into proper
IP address. 

## Check RabbitMQ server status

Execute 

    rabbitmqctl status

If the server is running properly, the outpu should
be similar with the following

    Status of node 'rabbit@rabbitmq-1' ...
[{pid,10413},
     {running_applications,[{rabbit,"RabbitMQ","3.3.5"},
                            {mnesia,"MNESIA  CXC 138 12","4.11"},
                            {os_mon,"CPO  CXC 138 46","2.2.14"},
                            {xmerl,"XML parser","1.3.6"},
                            {sasl,"SASL  CXC 138 11","2.3.4"},
                            {stdlib,"ERTS  CXC 138 10","1.19.4"},
                            {kernel,"ERTS  CXC 138 10","2.16.4"}]},
     {os,{unix,linux}},
     {erlang_version,"Erlang R16B03-1 (erts-5.10.4) [source] [64-bit] [async-threads:30] [hipe] [kernel-poll:true]\n"},
     {memory,[{total,34871408},
              {connection_procs,2720},
              {queue_procs,5440},
              {plugins,0},
              {other_proc,13215984},
              {mnesia,58144},
              {mgmt_db,0},
              {msg_index,33936},
              {other_ets,745304},
              {binary,13320},
              {code,16707114},
              {atom,602729},
              {other_system,3486717}]},
     {alarms,[]},
     {listeners,[{clustering,25672,"::"},{amqp,5672,"::"}]},
     {vm_memory_high_watermark,0.4},
     {vm_memory_limit,416371507},
     {disk_free_limit,50000000},
     {disk_free,52134936576},
     {file_descriptors,[{total_limit,924},
                        {total_used,3},
                        {sockets_limit,829},
                        {sockets_used,1}]},
     {processes,[{limit,1048576},{used,124}]},
     {run_queue,0},
     {uptime,2225}]
    ...done.


# Python development environment

- python 2.7
- pika 0.10.0

    pip install pika

# Simple Queue