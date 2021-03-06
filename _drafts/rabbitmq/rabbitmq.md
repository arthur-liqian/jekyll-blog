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

Setup a RabbitMQ server locally. One process sends message to the default
exchange which has no name, and messages are routed to a queue named "hello".
And a process receives and consumes message from "hello" queue.

The code sends one message:

    #!/usr/bin/env python

    from pika import BlockingConnection, ConnectionParameters

    connection = BlockingConnection(ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='', routing_key='hello', body='hello world')

    connection.close()

    print "Send 'hello world'"

The code receives and consumes message: 

    #!/usr/bin/env python
    
    from pika import BlockingConnection, ConnectionParameters
    
    connection = BlockingConnection(ConnectionParameters('localhost'))
    channel = connection.channel()
    
    channel.queue_declare(queue='hello')
    
    def callback(channel, method, properties, body):
            print "Received %s" % body
    
    
    channel.basic_consume(callback, queue='hello', no_ack=True)
    
    
    print "Waiting for messages."
    
    channel.start_consuming()

# exchange binding

an exchange could be bind to several queues.

- BlockingConnection class has serveral limitations. The channel object
    obtained from a BlockingConnection has a method `start_consuming`. This 
    method must be called, otherwise the message wouldn't be consumed. And
    this method blocks the current process/thread executing, and it doesn't 
    response to the thread interruption signal well. As a result, it is not 
    practical to use `BlockingConnection` class in multithreading.

- By default, the `no_ack` parameter of method `basic_consume` is `False`. That
    means a consumer should acknowledge the server the message has been 
    processed successfully. Otherwise, the server stores the message 
    consistently.

# multiple consumers share one queue

- the messages will be equally splited to all of the consumersed to all of the
    consumers
- the logic won't be impacted by the type of exchange

# default exchange

- A qeueu without public name can be used to receive message, when no exchange
    is explicitly declared. The exchange name parameter should be an empty
    string when `basic_publish` method is called, in that case. And receiver
    MUST NOT bind the queue to the default nameless exchange. That operation
    would cause an ACCESS_REFUSED error. When default exchange is used, the
    queue name is always used as routing key in the implicit queue binding. As
    a result, sender MUST always use target queue name as routing key when
    publish a message. Then the recommended practice is the queue name should 
    always be used as routing key to publish message, if no specific routing
    logic is employed. 

- the nameless default exchange is a direct exchange

# fanout exchange

Fanout exchange always redirects all of the messages to all of the queues bound
to it. The routing key in the binding, and the routing key associated to the
message sent is always ignored. As a result, it is meanlingless to assign 
routing key when fantout exchange is used.

# direct exchange

direct change always dispatches messages to queues by routing keys.

## multibinding

one direct exchange could be bound to multiple queues. During binding, routing
key is mandatory, and always used to filter the message to the queue. 

when multiple queues are bound to one exchange,  different queues could share
the same routing key. in such case, all of the queues whose bindings share the
same routing key, would always get all of the message associate with that 
routing key.

one queue could also be bound to multiple exchanges, and receives all of the 
messages from all of the bound exchanges, if the routing key matches the binding
definition.

one queue could also be bound to an exchange more than once. in that case, 
each binding definition could be assigned with different routing keys. with 
such kind of bindings, a queue could receive messages associated with more than
one kind of routing keys from one exchange. that also means consequencial 
binding definition doesn't overwrite the existing one. and the existing consumer
will also receive the message with the new routing key.

# multithreading

## BlockingConnection

- `BlockingConnection` object always employs `BlockingChannel` class to handle
    the channel logic.
- `BlockingChannel` object always blocks on `startConsuming` method, which
    actually blocks on `BlockingConnection`'s `__flush_output` method. 
    `__flush_output` method always loop the socket connection to get the 
    incomming message, until the speific condition is met.
- According to the interface doc, `BlockingChannel`'s `stopConsuming` method
    cancels all of the consumers registered on the current channel, and notify
    the `start_consuming` method to exit the blocking loop. However, the 
    `start_consuming` method still blocks, after the `stop_consuming` is 
    called. The `start_consuming` loop stopping condition should be 
    clearified.

# TODO
- the order of exchange and queue declaration
    - what will happen if queue is declared before exchange, and being bound to
        the exchange
- the different type of exchange, fanout, direct, etc.
    - there are 2 mandatory exchange types:
        - direct
        - fanout
- the projection between exchange and queue 
- routing key
- queue
    - persistency type
        - durable
        - temporary
        - auto-deleted
- message ackownledge
    - suceeded
    - failed
    - cancel
    - timeout
- asynchronized message processing
    - SelectConnection
- exchange and queue definition between sender and receiver
    - the exchange's type can't be changed after declaration. how to make sender
    and receiver won't conflict with each other
- message life cycle and status 
- performance
    - sending and receiving latency
    - message size
    - concurrency