#!/usr/bin/python
#File: receiver.py
 
import kombu
 
connection = kombu.BrokerConnection('librabbitmq://localhost')
simple_queue = connection.SimpleQueue('test')
 
print '[*] waiting for messages, if exit press CTRL+C'
 
def message_process(body, message):
    print '[receive]: %s' % body
    message.ack()
 
simple_queue.consumer.callbacks = [message_process] 
simple_queue.get()
simple_queue.close()
