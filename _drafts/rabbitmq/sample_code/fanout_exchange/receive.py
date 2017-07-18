#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

exchange_name = "fanout_exchange"

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=exchange_name, type='fanout')
# when no queue name is given, a random unique name will be generated. The 
# fanout exchange always copies and dispatches each message to all of the 
# bound queues. In order to demonstrate that behavior, each receiver process
# requires a separated queue, so we leverage the automitcally generated queues.
queue_declaring_result = channel.queue_declare()
queue_name = queue_declaring_result.method.queue

channel.queue_bind(exchange=exchange_name, queue=queue_name)

def callback(channel, method, properties, body):
    print "[%s]\tReceived Message: %s" % (queue_name, body)


channel.basic_consume(callback, queue=queue_name, no_ack=True)

print "[%s]\tStart receiving messages!" % queue_name
channel.start_consuming()
