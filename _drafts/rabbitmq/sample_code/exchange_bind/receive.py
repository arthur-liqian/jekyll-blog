#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

EXCHANGE_NAME = 'channel_binding_exchange'
QUEUE_NAME = 'channel_binding_queue'
ROUTING_KEY = 'channel_binding_routing_key'

connection = BlockingConnection(ConnectionParameters('localhost'))

def log(prefix, message):
    print "[%s]\t%s" % (prefix, message)

class Receiver(object):

    def __init__(self, id, connection):
        self.id = id
        self.connection = connection
        self.channel = self.connection.channel()

        self.channel.exchange_declare(EXCHANGE_NAME)
        self.channel.queue_declare(queue=QUEUE_NAME)

        self.channel.queue_bind(exchange=EXCHANGE_NAME,
                queue=QUEUE_NAME,
                routing_key=ROUTING_KEY)

    def start(self):
        self.channel.basic_consume(self.on_message,
                queue=QUEUE_NAME,
                no_ack=True) # by defult, no_ack is False, and the message
                             # should be always acknowledged explicitly
                             # Message ackonwledging will be demonstrated
                             # in other sample

        self.log("Start Consuming message")
        # the channel object obtained from BlockingConnection always blocks
        # the current process/thread from executing when its start_consuming
        # is called
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        self.log(body)

    def log(self, message):
        log("Reciever-%i" % self.id, message)


receiver = Receiver(1, connection)
receiver.start()
