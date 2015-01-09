#!/bin/sh
# This script will start two iperf containers, connected by an openvswitch bridge.

echo "Required: openvswitch, docker, ovs-docker"

# Check requisites here...TBD
#[ ! -x ovs-docker ] && \
#    echo "Required ovs-docker script is not found" && \
#    echo "Download from https://github.com/openvswitch/ovs/raw/master/utilities/ovs-docker" && \
#    exit;

echo "Creating an ovs bridge ovs..."
sudo ovs-vsctl --may-exist add-br br0

echo "Configuring port ovs to 172.17.0.1/16..."
sudo ifconfig br0 172.17.0.1/16

echo "Boot two raw containers without networking..."
cid1=`sudo docker run -d --net=none --privileged=true gdanii/iperf:latest /bin/sh -c "while true; do echo active; sleep 30; done"`
cid2=`sudo docker run -d --net=none --privileged=true gdanii/iperf:latest /bin/sh -c "while true; do echo active; sleep 30; done"`
echo $cid1, $cid2

echo "Adding nic insides containers, and binding to the ovs bridge"
sudo ovs-docker add-port br0 eth0 $cid1
sudo ovs-docker add-port br0 eth0 $cid2

echo "Setting nic IP for containers..."
sudo docker exec $cid1 ifconfig eth0 172.17.0.2/16
sudo docker exec $cid2 ifconfig eth0 172.17.0.3/16

echo "Starting iperf server on container 1"
sudo docker exec $cid1 iperf -s &

echo "Starting iperf server on container 2"
sudo docker exec $cid2 iperf -t 20 -c 172.17.0.2


echo "Removing the binding interfaces"
sudo ovs-docker del-port br0 eth0 $cid1
sudo ovs-docker del-port br0 eth0 $cid2

echo "Killing the containers"
sudo docker rm -f $cid1 $cid2
