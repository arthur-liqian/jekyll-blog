#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters
from threading import Thread

EXCHANGE_NAME = 'channel_binding_exchange'
QUEUE_NAME = 'channel_binding_queue'
ROUTING_KEYS = ['red', 'green', 'yellow']

connection = BlockingConnection(ConnectionParameters('localhost'))

def log(prefix, message):
    print "[%s]\t%s" % (prefix, message)

class Sender(Thread):

    def __init__(self, id, connection):
        Thread.__init__(self)

        self.id = id
        self.connection = connection
        self.channel = self.connection.channel()

        self.channel.exchange_declare(EXCHANGE_NAME)

    def run(self):
        self.log("Start sending message!")
        for i in range(20):
            routing_key = ROUTING_KEYS[i % len(ROUTING_KEYS)]

            self.channel.basic_publish(exchange=EXCHANGE_NAME, 
                    routing_key=routing_key, 
                    body='Message-%i from sender-%i with routing key %s'
                            % (i, self.id, routing_key))
            self.log("Sent message-%i with routing key $s" % (i, routing_key))
        
        self.log("Finish sending message!")
    
    def log(self, message):
        log("Sender-%i" % self.id, message)

sender = Sender(1, connection)

sender.start()
