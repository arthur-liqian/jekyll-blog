#! /usr/bin/env python

from threading import Thread
from pika import BlockingConnection, ConnectionParameters

connection = BlockingConnection(ConnectionParameters('localhost'))
exchange = "multithread_exchange"
routing_key = "multithread"

class Sender(Thread):

    def __init__(self, id, connection, exchange, routing_key):
        Thread.__init__(self)

        self.id = id

        self.connection = connection
        self.exchange = exchange
        self.routing_key = routing_key

        self.channel = self.connection.channel()
        self.channel.exchange_declare(self.exchange)

    def run(self):
        self.log("Starts sending message!")

        for i in range(1000):
            message = "Message-%i from Sender-%i" % (i, self.id)

            self.channel.basic_publish(exchange=self.exchange,
                    routing_key=self.routing_key,
                    body=message)

        self.log("Finished sending message!")

    def log(self, message):
        print "[Sender-%i]\t %s" % (self.id, message)

for i in range(100):
    sender = Sender(i, connection, exchange, routing_key)

    sender.start()
    sender.join()

connection.close()

print "Sending Process Finished!"
