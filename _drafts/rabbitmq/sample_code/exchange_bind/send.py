#!/usr/bin/env python

from pika import BlockingConnection, ConnectionParameters
from threading import Thread

EXCHANGE_NAME = 'channel_binding_exchange'
QUEUE_NAME = 'channel_binding_queue'
ROUTING_KEY = 'channel_binding_routing_key'

connection = BlockingConnection(ConnectionParameters('localhost'))

def log(prefix, message):
    print "[%s]\t%s" % (prefix, message)

class Receiver(Thread):

    def __init__(self, id, connection):
        Thread.__init__(self)

        self.id = id
        self.connection = connection
        self.channel = self.connection.channel()

        self.channel.exchange_declare(EXCHANGE_NAME)
        self.channel.queue_declare(queue=QUEUE_NAME)

        self.channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=ROUTING_KEY)

    def run(self):
        self.channel.basic_consume(self.on_message, queue=QUEUE_NAME)
        self.channel.start_consuming()
        self.log("Start Consuming message")

    def on_message(self, ch, method, properties, body):
        self.log(body)

    def log(self, message):
        log("Reciever-%i" % self.id, message)

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
            import time; time.sleep(5)
        
        self.log("Finish sending message!")
    
    def log(self, message):
        log("Sender-%i" % self.id, message)

receiver = Receiver(1, connection)
sender = Sender(1, connection)

#receiver.start()
receiver.run()
sender.start()
