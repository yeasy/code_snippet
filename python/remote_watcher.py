#!/usr/bin/python
# Daemon script. 
# Watch the specified file on remote host, 
# trigger action when there finds some keyword in it.

import sys
sys.path.append("..")

import os
import string
import datetime
import urllib
import simplejson as json
import time

remote_ip="10.0.1.2"
remote_file="/var/log/message"

cache_file="cache"
cache_file_bk="cache.bak"

GMT_FORMAT= '[%Y-%m-%d %H:%M:%S] '
keyword = '[*event*]'
nLoop = 500000
nEvent = 0

work_path = os.path.split(os.path.realpath(__file__))[0]+"/"
os.system("cd "+work_path)

print "Get remote file (Need automatical auth first)."
os.system("scp root@%s:%s %s 2>&1 > /dev/null" %(remote_ip,remote_file,cache_file))
os.system("cp %s %s" %(cache_file,cache_file_bk))

def trigger_action(line):
    """
    Do some process when an event happens
    @param line: The line triggering the event
    """
    titlelist = line.split(' ')
    pass

def main():
    #Recursively obtain and parse the log msg, to find alert.
    while nLoop > 0:
        os.system("rm -f diff.txt 2>&1 > /dev/null")
        os.system("scp root@%s:%s %s 2>&1 > /dev/null" %(remote_ip,remote_file,cache_file))
        os.system("diff %s %s >> diff.txt" %(cache_file,cache_file_bk))
        f = open("diff.txt")
        for line in f:
            if len(line) == 0:
                break
            if line.find(keyword) > 0:
                nEvent = nEvent + 1
                trigger_action(line)

        os.system("cp %s %s" %(cache_file,cache_file_bk))
        os.system("sleep 2")
        nLoop = nLoop - 1
    print "%d events triggered" % nEvent

if __name__ == '__main__':
    main()
