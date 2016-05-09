#code_snippet
============

Some simple but useful source codes, scripts or templates, on networking, programming, algorithm, etc.

Most of them are written by me, while some one may be collected from Internet or modified based or public-available codes.

All files are free to use, distribute or modify, with keeping the declarition part on the file head. However, the authors WILL NOT be responsible for any result by these files. If you think there might be some one affecting your privilege, please let me know.

## autopreview
A light script plugin for Vim that could automatically preview the definition of variables or functions in a tiny window like source insight. Also be hosted at the [vim homepage](http://www.vim.org/scripts/script.php?script_id=2228).

## algorithm
Some code blocks for test algorithms, such as sorting, searching, etc..

## bf-gdt
Example to show how to use the bloom-filter based gdt data structure.

## cpu
Get overall cpu utilization at linux platform.

## Docker
Some docker related scripts and tools.
### docker\_cleanup
Do some cleanup work on Docker Host, e.g., removing stopped containers and untagged images.

### ovs\_perf
Test two containers connecting through OpenvSwitch with iperf

### save\_all\_images
Save all local Docker images into tar.gz files.

### restore\_images
This script will load into the tar.gz files as images.

## ether\_bridge
Connect to network interface and forward ethernet packets between them bidirectionally, supporting options.

## getIP
Some scripts to get local ip address of the network interfaces.

## getopt
Show how to use getopt functions.

## io
Test read and write functions.

## json
Example to show how to use json encoding/decoding in python.

## mcast
Test the multi-cast packet sending and receiving, using a thread separately.

## Makefile.template
Simple template of Makefile.

## netlink
Test bidirectional communication between userspace and kernelspace, using low-level netlink APIs in the userspace, and libnl APIs in the kernelspace.

## [python](python)
Simple codes to show how to use python libraries, e.g., regrex, encoding.
### amqp
Demo the usage of AMQP by the kombu and pika.
###  concurrency
Some scripts on concurrency programming, such as threading, eventlet...
###  gitbook\_gen
Generate an initialized gitbook project based on the given source code path.
### httpserver
A simple webserver by python, which tracks request number of each visitor's IP address.
### mqtt
Demo the usage of MQTT.
### prefixCutter
Calculate the cut prefixes by given two prefixes.
### remote\_watcher
Watch the specified file on remote, trigger action when there finds keyword in it.
### sm\_watcher
Track (and filter) the board articles on the given url (newsmth now), and show them in a webpage in realtime (using jquery and HTML5 websocket).
### wsgi
A demo to show how to use wsgi and paste deployment to provide a web service. 
Run `python server.py` and get the version information by visiting localhost:8080.

## [remote](remote)
### remoteAuth.sh
An ssh authorized script, which enables you to login into remote host automatically without passwd inputing.
### pull\_agent.sh
Daemon agent to pull some content from remote host, and do action after check changes.
### push\_agent.sh
Daemon agent to push some msg to remote host file.

## [sendRawPkt](sendRawPkt)
Example to show how to construct a raw socket packet, with manually setting the mac, ip and udp header.


## shell
Useful shell scripts.

## [system](system)
Some system related tools, such as init a fresh os.
### getweb.sh
Simple but powerful script, which can automatically download a website by URL and save it to local directory for offline reference.
### rm.sh
A much safer rm script, which can automatically backup removed files, in case deleting useful data (beta version).
### nss
This script will show all ip address inside each network namespace. If give a parameter, then it will show the network namespace containing the key. This is useful for openstack debugging.
### service
Example of a system service script in Debian/Ubuntu system, supporting running complicated command with arbitrary parameters.
