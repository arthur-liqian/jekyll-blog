#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

queue_name = 'queue_name_as_routing_key_exchange'

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue_name)

def callback(channel, method, properties, body):
	print "Received %s" % body


channel.basic_consume(callback, queue=queue_name, no_ack=True)


print "Waiting for messages." 

channel.start_consuming()
