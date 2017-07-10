#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_publish(exchange='', routing_key='hello', body='hello world')

connection.close()

print "Send 'hello world'"

