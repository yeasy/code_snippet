#!/usr/bin/python
#Daemon script. Watch on the specific folder (e.g., /tmp/file), 
#Parse the msg and do processing when it changes.
#Usage: ./pull_agent.py host_ip file

import sys
import os
import string
import datetime
import urllib
import simplejson as json

#the user/ip of the remote host that needs to be monitored
user="root"
#remotehost="9.186.105.166"
#remotefile="/tmp/cpu.dat"

if len(sys.argv) < 3:
    sys.exit('Usage: %s host_ip file' % sys.argv[0])

remotehost=sys.argv[1]
remotefile=sys.argv[2]

localfile=remotehost+"_"+remotefile.replace("/","_")
bakfile=localfile+".bak"
tmpfile=localfile+".tmp"
difffile=localfile+".diff"
action="echo 'do some action'"

tmp_path = os.path.split(os.path.realpath(__file__))[0]+"/tmp/"
if not os.path.exists("tmp"):
    os.makedirs("tmp");

os.chdir("tmp")

#cp remote file to local 
os.system("scp %s@%s:%s ./%s 2>&1 > /dev/null" %(user,remotehost,remotefile,tmpfile))
os.system("sort -n %s |uniq > %s" %(tmpfile,localfile))
os.system("cp %s %s" %(localfile,bakfile))

nLoop = 3
while nLoop > 0:
    os.system("rm -f %s" %(difffile))
    os.system("scp %s@%s:%s ./%s 2>&1 > /dev/null" %(user,remotehost,remotefile,tmpfile))
    os.system("sort -n %s |uniq > %s" %(tmpfile,localfile))
    os.system("diff %s %s > %s" %(localfile,bakfile,difffile))
    f = file(difffile)
    line  = f.readline();
    if len(line) != 0:
        os.system("%s" %(action))
    f.close()
    os.system("cp %s %s" %(localfile,bakfile))
    os.system("echo ...")
    os.system("sleep 2")
    nLoop = nLoop - 1
