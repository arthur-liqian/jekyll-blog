#! /usr/bin/env python

from optparse import OptionParser
from pika import BlockingConnection, ConnectionParameters

optionParser = OptionParser(add_help_option=False)
optionParser.add_option('-x', dest='exchange', action='store')
optionParser.add_option('-k', dest='routing_keys', action='store')

(option, args) = optionParser.parse_args()

exchange_name = option.exchange
routing_keys = option.routing_keys.split(',')

sender_id = args[0]

connection = BlockingConnection(ConnectionParameters('localhost'))

def log(prefix, message):
    print '[%s]\t%s' % (prefix, message)

class Sender(object):

    def __init__(self, id, connection, exchange, routing_keys):
        self.id = id
        self.connection = connection
        self.exchange = exchange
        self.routing_keys = routing_keys

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self.exchange, type='direct')

    def start(self):
        self.log("Start sending message through exchange %s with routing keys %s"
                % (self.exchange, self.routing_keys))
        
        for i in range(10):
            routing_key = self.routing_keys[i % len(self.routing_keys)]

            message = 'Message-%s from Sender-%s with routing key %s'\
                    % (i, self.id, routing_key)
            self.channel.basic_publish(exchange=self.exchange,
                    routing_key=routing_key,
                    body=message)
            
            self.log('Sending message-%s with routing key %s'
                    % (i, routing_key))
        
        self.log('Finish sending messages!')

    def log(self, message):
        log('Sender-%s' % self.id, message)

sender = Sender(sender_id, connection, exchange_name, routing_keys)
sender.start()
