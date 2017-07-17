#!/use/bin/env python

from pika import BlockingConnection, ConnectionParameters

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

def callback(channel, method, properties, body):
	print "Received %s" % body


channel.basic_consume(callback, queue='hello', no_ack=True)


print "Waiting for messages." 

channel.start_consuming()