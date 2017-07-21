#! /usr/bin/env python

import sys
from threading import Thread, Condition
from time import sleep

class SleepThread(Thread):

    def __init__(self):
        Thread.__init__(self)

        self.__stopped = False

    def run(self):
        while not self.__stopped:
            sleep(5)
            print '.'

    def stop(self):
        self.__stopped = True

t = SleepThread()
t.start()

#condition = Condition()
try:
    sleep(65535)
except KeyboardInterrupt:
    print 'Main process is interrupted!'
    t.stop()
#try:
    #condition.acquire()
    #print 'Main process starts waiting'
    #condition.wait()
#except KeyboardInterrupt:
    #print 'Main process is interrupted!'

print 'Main process is finished'


