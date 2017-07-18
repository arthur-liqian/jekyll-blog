#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

exchange_name = "queue_shared_exchange"
queue_name = "queue_shared"

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, type="direct")

print "[Sender]\tStart sending message"

for i in range(10):
    channel.basic_publish(exchange=exchange_name,
            routing_key='',
            body='Message-%i' % i)
    print "[Sender]\tSent Message-%i" % i

print "[Sender]\tFinish sending message"
connection.close()

