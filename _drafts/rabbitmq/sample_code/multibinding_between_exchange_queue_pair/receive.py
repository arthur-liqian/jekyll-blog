#!/usr/bin/env python

import sys

from pika import BlockingConnection, ConnectionParameters

EXCHANGE_NAME = 'channel_binding_exchange'

connection = BlockingConnection(ConnectionParameters('localhost'))

def log(prefix, message):
    print "[%s]\t%s" % (prefix, message)

class Receiver(object):

    def __init__(self, id, connection, routing_keys):
        self.id = id
        self.connection = connection
        self.channel = self.connection.channel()

        self.channel.exchange_declare(EXCHANGE_NAME)
        result = self.channel.queue_declare()

        self.queue_name = result.method.queue

        self.routing_keys = routing_keys

        for routing_key in self.routing_keys:
            self.channel.queue_bind(exchange=EXCHANGE_NAME,
                    queue=self.queue_name,
                    routing_key=routing_key)

    def start(self):
        self.channel.basic_consume(self.on_message,
                queue=self.queue_name,
                no_ack=True)

        self.log("Start Consuming message with routing keys %s"
                % self.routing_keys)
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        self.log(body)

    def log(self, message):
        log("Reciever-%s" % self.id, message)

receiver_id = sys.argv[1]
routing_key = sys.argv[2]

receiver = Receiver(receiver_id, connection, routing_key)
receiver.start()
