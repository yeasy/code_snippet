#!/usr/bin/python
#File: sender.py
#prerequisites: rabbitmq-server python-rabbitmq python-kombu
 
import kombu
import sys 
 
connection = kombu.Connection('librabbitmq://localhost')
simple_queue = connection.SimpleQueue('test')
 
if len(sys.argv) < 2:
    print 'message is empty!'
    sys.exit(0)
 
message = sys.argv[1]
simple_queue.put(message)
print '[send]: ' + message + '\n'
simple_queue.close()
