#!/use/bin/env python

from threading import Thread, Lock, Condition
from time import time

MAX_SIZE=1000

QUEUE = []
QUEUE_CONDITION = Condition()

class Producer(Thread):

    def __init__(self, id, queue, max_size, queue_condition):
        Thread.__init__(self)
        self.id = id
        self.queue = queue
        self.max_size = max_size
        self.queue_condition =  queue_condition

    def run(self):
        print "[Producer-%i]\t starts running!" % self.id
        self.queue_condition.acquire()

        for i in range(10000):
            while len(self.queue) >= self.max_size:
                print "[Producer-%i]\tThe queue reaches its max size, waiting for consumer" % i
                self.queue_condition.wait()

            self.queue.append("Message-%i from Producer-%i" % (i, self.id))    
            print "[Producer-%i]\tPut Message-%i" % (self.id, i)

            self.queue_condition.notifyAll()
        
        self.queue_condition.release()

class Consumer(Thread):

    def __init__(self, id, queue, queue_condition):
        Thread.__init__(self)
        self.id = id
        self.queue = queue
        self.queue_condition = queue_condition


    def run(self):
        print "[Consumer-%i]\t starts running!" % self.id
        self.queue_condition.acquire()

        while True:
            while len(self.queue) <= 0:
                interval = 30
                start_time = time()

                print "[Consumer-%i]\tThe queue is empty, waiting for producer" % self.id
                self.queue_condition.wait(interval)

                if time() - start_time > interval:
                    print "[Consumer-%i]\tThe consumer exits" % self.id
                    self.queue_condition.release()
                    return
            
            message = self.queue.pop()
            print "[Consumer-%i]\tMessage: %s" % (self.id, message)

            self.queue_condition.notify_all()

producers = []
consumers = []

for i in range(10):
    producer = Producer(i, QUEUE, MAX_SIZE, QUEUE_CONDITION)
    producer.start()

    producers.append(producer)

for i in range(5):
    consumer = Consumer(i, QUEUE, QUEUE_CONDITION)
    consumer.start()

    consumers.append(consumer)

for producer in producers:
    producer.join()

for consumer in consumers:
    consumer.join()