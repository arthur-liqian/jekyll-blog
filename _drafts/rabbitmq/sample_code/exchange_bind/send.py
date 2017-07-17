#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters
from threading import Thread

EXCHANGE_NAME = 'channel_binding_exchange'
QUEUE_NAME = 'channel_binding_queue'
ROUTING_KEY = 'channel_binding_routing_key'

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
        for i in range(10):
            self.channel.basic_publish(exchange=EXCHANGE_NAME, 
                    routing_key=ROUTING_KEY, 
                    body='Message-%i from sender-%i' % (i, self.id))
            self.log("Sent message-%i" % i)
        
        self.log("Finish sending message!")
    
    def log(self, message):
        log("Sender-%i" % self.id, message)

sender = Sender(1, connection)

sender.start()
