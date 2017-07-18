#!/usr/bin/env python

import sys

from pika import BlockingConnection, ConnectionParameters

EXCHANGE_NAME = 'channel_binding_exchange'
QUEUE_NAME = 'channel_binding_queue'

connection = BlockingConnection(ConnectionParameters('localhost'))

def log(prefix, message):
    print "[%s]\t%s" % (prefix, message)

class Receiver(object):

    def __init__(self, id, connection, routing_key):
        self.id = id
        self.connection = connection
        self.channel = self.connection.channel()

        self.channel.exchange_declare(EXCHANGE_NAME)
        self.channel.queue_declare(queue=QUEUE_NAME)

        self.channel.queue_bind(exchange=EXCHANGE_NAME,
                queue=QUEUE_NAME,
                routing_key=routing_key)

    def start(self):
        self.channel.basic_consume(self.on_message,
                queue=QUEUE_NAME,
                no_ack=True)

        self.log("Start Consuming message")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        self.log(body)

    def log(self, message):
        log("Reciever-%i" % self.id, message)

routing_key = sys.argv[1]

receiver = Receiver(1, connection)
receiver.start()
