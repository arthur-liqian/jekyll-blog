#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

exchange_name = "fanout_exchange"

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=exchange_name, type='fanout')
queue_name = channel.queue_declare()

channel.qeueu_bind(exchange=exchange_name, qeueu=queue_name)

def callback(channel, method, properties, body):
    print "[%s]\tReceived Message: %s" % (queue_name, body)


channel.basic_consume(callback, queue=queue_name, no_ack=True)

print "[%s]\tStart receiving messages!" % queue_name
channel.start_consuming()
