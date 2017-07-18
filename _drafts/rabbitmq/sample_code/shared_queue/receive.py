#!/usr/bin/env python

import sys
from pika import BlockingConnection, ConnectionParameters

receiver_id = sys.argv[1]

exchange_name = "queue_shared_exchange"
queue_name = "queue_shared"

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=exchange_name, type="direct")
channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='')

def callback(channel, method, properties, body):
    print "[Receiver-%s]\tReceived %s" % (receiver_id, body)


channel.basic_consume(callback, queue=queue_name, no_ack=True)

print "[Receiver-%s]\tWaiting for message." % receiver_id
channel.start_consuming()
