#! /usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

exchange_name = 'fanout_routing_key_exchange'
queue_name = 'fanout_routing_key_queue'

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=exchange_name, type='fanout')
channel.queue_declare(queue=queue_name)

channel.queue_bind(exchange=exchange_name,
        queue=queue_name, routing_key='another_key')

def consume_callback(ch, method, properties, body):
    print "Received Message: %s" % body

channel.basic_consume(consume_callback, queue=queue_name, no_ack=True)

print 'Start consuming message'

channel.start_consuming()