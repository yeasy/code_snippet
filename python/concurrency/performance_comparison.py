# -*- coding:utf-8 -*-
__author__ = 'baohua'

def test(i,j):
    if i+j < i-j:
        return i+j

if __name__ == '__main__':
    import threading, time
    t0 = time.time()
    for i in range(10000):
        t = threading.Thread(target=test, args = (i,i+1))
        t.start()
    print "Threading: %.3fs taken" % (time.time() - t0)

    import eventlet, time
    eventlet.monkey_patch()

    t0 = time.time()
    pool = eventlet.GreenPool()
    for i in range(10000):
        pool.spawn(test, i, i+1)
    pool.waitall()
    print "Eventlet: %.3fs taken" % (time.time() - t0)
