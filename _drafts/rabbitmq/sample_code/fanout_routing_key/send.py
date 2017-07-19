#! /usr/bin/env python

from pika import BlockingConnection, ConnectionParameters

exchange_name = 'fanout_routing_key_exchange'

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=exchange_name, type='fanout')

channel.basic_publish(exchange=exchange_name,
        routing_key='fanout_routing_key',
        body='Message from fanout exchange with routing key fanout_routing_key')

print 'Sent message with routing key to a fanout exchange'

connection.close()
