#!/use/bin/env python

from pika import BlockingConnection, ConnectionParameters

routing_key = "multithread"
exchange = "multithread_exchange"
queue = "multithread_queue"

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue=queue)
channel.queue_bind(exchange=exchange, queue=queue)

def callback(channel, method, properties, body):
	print "Received %s" % body


channel.basic_consume(callback, queue='hello', no_ack=True)


print "Waiting for messages." 

channel.start_consuming()