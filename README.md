Code Snippet
============

Some simple but useful source codes, scripts or templates, on networking, programming, algorithm, etc.

Most of them are written by me, while some one may be collected from Internet or modified based or public-available codes.

All files are free to use, distribute or modify, with keeping the declare part on the file head. However, the authors WILL NOT be responsible for any result by these files. If you think there might be some one affecting your privilege, please let me know.


## [algorithm](algorithm)
Some code blocks for test algorithms, such as sorting, searching, etc..

Name | Description
-- | --
bf-gdt | Example to show how to use the bloom-filter based gdt data structure.
bit_op | show operation on bit
bitmap | show usage of bitmap
sort | sorting
match | searching

## [C](c)

C programing.

Name | Description
-- | --
getopt | Show how to use getopt functions.
io | Test read and write functions.
mcast | Test the multi-cast packet sending and receiving, using a thread separately.
[sendRawPkt](c/sendRawPkt) | Example to show how to construct a raw socket packet, with manually setting the mac, ip and udp header.

## [Docker](docker)
Some docker related scripts and tools.

Name | Description
-- | --
docker_cleanup | Do some cleanup work on Docker Host, e.g., removing stopped containers and untagged images.
ovs_perf | Test two containers connecting through OpenvSwitch with iperf
save_all_images | Save all local Docker images into tar.gz files.
restore_images | This script will load into the tar.gz files as images.

## [golang](golnag)
Some golang examples

Name | Description
-- | --
plugin | Demo how to use plugin to generate a .so file and then load it.
grpc | Demo how to use gRPC with the go module.

## [programing](programing)
Some simple tools to help programing more efficiently.

Name | Description
-- | --
autopreview | A light script plugin for Vim that could automatically preview the definition of variables or functions in a tiny window like source insight. Also be hosted at the [vim homepage](http://www.vim.org/scripts/script.php?script_id=2228).
Makefile.template | Simple template of Makefile.

## [python](python)
Simple codes to show how to use python libraries, e.g., regrex, encoding.

Name | Description
-- | --
amqp | Demo the usage of AMQP by the kombu and pika.
concurrency | Some scripts on concurrency programming, such as threading, eventlet...
gitbook_gen | Generate an initialized gitbook project based on the given source code path.
json | Example to show how to use json encoding/decoding in python.
json_flatter | Flat the structure of json files under given path.
mqtt | Demo the usage of MQTT.
netlink | Test bidirectional communication between userspace and kernelspace, using low-level netlink APIs in the userspace, and libnl APIs in the kernelspace.
prefixCutter | Calculate the cut prefixes by given two prefixes.
pull_agent.sh | Daemon agent to pull some content from remote host using scp, and do action after check changes.
push_agent.sh | Daemon agent to push some msg to remote host file.
remote_watcher | Watch the specified file on remote using scp, trigger action when there finds keyword in it.
stat_parse | Parse the ifconfig results and get the pkts/bytes number.
tls_server | A simple tls server by python, which enable tls, and allow server to check client's certificate.
wsgi | A demo to show how to use wsgi and paste deployment to provide a web service. Run `python server.py` and get the version information by visiting localhost:8080.

## [shell](shell)
Useful shell functions.

```bash
 source functions
```

## [security](security)
Demo of usage of security tools including cfssl and openssl.

Name | Description
-- | --
[cfssl](security/cfssl) | Use cfssl to generate certificate.
[openssl](security/openssl) | Use openssl to generate certificate and serve a website with TLS.

## [system](system)
Some system related tools, such as init a fresh os.

Name | Description
-- | --
cpu | Get overall cpu utilization at linux platform.
ether_bridge | Connect to network interface and forward ethernet packets between them bidirectionally, supporting options.
getIP | Some scripts to get local ip address of the network interfaces.
rm.sh | A much safer rm script, which can automatically backup removed files, in case deleting useful data (beta version).
[nss](system/nss) | This script will show all ip address inside each network namespace. If give a parameter, then it will show the network namespace containing the key. This is useful for openstack debugging.
service | Example of a system service script in Debian/Ubuntu system, supporting running complicated command with arbitrary parameters.
socket | Example of socket programing using C
sysctl.conf | Optimized configuration for /etc/sysctl.conf.
limits.conf | Optimized configuration for /etc/security/limits.conf.

## [Web](web)

Website related.

Name | Description
-- | --
getweb.sh | Simple but powerful script, which can automatically download a website by URL and save it to local directory for offline reference.
httpserver | A simple webserver by python, which tracks request number of each visitor's IP address.
sm_watcher | Track (and filter) the board articles on the given url (newsmth now), and show them in a webpage in realtime (using jquery and HTML5 websocket).
ss_watcher | Auto fetch proxy information and update local config.

