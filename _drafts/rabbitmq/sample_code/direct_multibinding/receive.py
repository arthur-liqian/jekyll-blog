#! /usr/bin/env python

from optparse import OptionParser
from pika import BlockingConnection, ConnectionParameters

def log(prefix, message):
    print '[%s]\t%s' % (prefix, message)

class Binding(object):

    def __init__(self, binding_str):
        binding_strs = binding_str.split('-')

        self.exchange = binding_strs[0]
        self.routing_keys = binding_strs[1].split(',')

class Receiver(object):

    def __init__(self, id, connection, bindings):
        self.id = id
        self.connection = connection
        self.bindings = bindings

        self.channel = self.connection.channel()
        self.queue_name = self.channel.queue_declare().method.queue

        for binding in self.bindings:
            self.channel.exchange_declare(exchange=binding.exchange,
                    type='direct')
            
            for routing_key in binding.routing_keys:
                self.channel.queue_bind(exchange=binding.exchange,
                        qeueu=self.queue_name
                        routing_key=routing_key)
                self.log("Bouding queue %s to exchange %s with routing key %s"
                        % (self.queue_name, binding.exchange, routing_key))

    def start(self):
        self.channel.basic_consuming(self.__on_message,
                queue=self.queue_name,
                no_ack=True)
        self.log('Start consuming message!')
        self.channel.start_consuming()
    
    def __on_message(self, ch, method, properties, body):
        self.log(body)

    def log(self, message)
        log('Receiver-%s' % self.id, message)

optionParser = OptionParser(add_help_option=False)
optionParser.add_option('-b', dest='binding', action='append')

(option, args) = optionParser.parse_args()
receiver_id = args[0]
bindings = []

for binding_str in option['binding']:
    bindings.append(Binding(binding_str))

connection = BlockingConnection(ConnectionParameters('localhost'))

receiver = Receiver(receiver_id, connection, bindings)