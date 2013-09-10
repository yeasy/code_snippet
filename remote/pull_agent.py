#!/usr/bin/python
#Daemon script. Watch on the specific folder (e.g., /tmp/file), 
#Parse the msg and do processing when it changes.

import sys
import os
import string
import datetime
import urllib
import simplejson as json

#the user/ip of the remote host that needs to be monitored
user="root"
remotehost="192.168.57.10"
remotefile="/tmp/cpu.dat"

localfile=remotehost+"_"+remotefile.replace("/","_")
action="echo 'do some action'"

work_path = os.path.split(os.path.realpath(__file__))[0]+"/"
os.system("cd "+work_path)

#cp remote file to local 
os.system("scp %s@%s:%s ./%s 2>&1 > /dev/null" %(user,remotehost,remotefile,localfile))
os.system("cp %s %s" %(localfile,localfile+".bak"))

nLoop = 100
while nLoop > 0:
    os.system("rm -f diff.txt")
    os.system("scp %s@%s:%s ./%s 2>&1 > /dev/null" %(user,remotehost,remotefile,localfile))
    os.system("diff %s %s >> diff.txt" %(localfile,localfile+".bak"))
    f = file("diff.txt")
    line  = f.readline();
    if len(line) != 0:
        os.system("%s" %(action))
    f.close()
    os.system("cp %s %s" %(localfile,localfile+".bak"))
    os.system("echo ...")
    os.system("sleep 2")
    nLoop = nLoop - 1
