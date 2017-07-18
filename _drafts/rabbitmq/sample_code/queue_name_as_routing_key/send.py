#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

queue_name = 'queue_name_as_routing_key_exchange'

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.basic_publish(exchange='', routing_key='', body='hello world')

connection.close()

print "Send 'hello world'"

