#! /use/bin/env python

from threading import Thread
from pika import BlockingConnection, ConnectionParameters

EXCHANGE_NAME = 'multithread_receiver_exchange'
QUEUE_NAME = 'multithread_receiver_queue'
ROUTING_KEY = 'multithread_receiver_routing_key'

def log(prefix, message):
    print '[%s]\t%s' % (prefix, message)

class Receiver(Thread):

    def __init__(self, id, connection, exchange, queue, routing_key):
        Thread.__init__(self)

        self.id = id
        self.connection = connection
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self.exchange, type='direct')
        self.channel.queue_declare(queue=self.queue)

        self.channel.queue_bind(exchange=self.exchange,
                queue=self.queue,
                routing_key=self.routing_key)

    def run(self):
        self.channel.basic_consume(self.on_message,
                queue=self.queue,
                no_ack=True)
        
        self.log("Start Consuming message!")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        self.log(body)

    def log(self, message):
        log('Multithread-Receiver-%s' % self.id, message)

connection = BlockingConnection(ConnectionParameters('localhost'))

receiver = Receiver(1, connection, EXCHANGE_NAME, QUEUE_NAME, ROUTING_KEY)

receiver.start()
receiver.join()
