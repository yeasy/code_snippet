#!/bin/sh
# This script will start two iperf containers, connected by an openvswitch bridge.

OVS_BR=br0
PORT_SERVER="port_server"
PORT_CLIENT="port_client"
PORT_MIRROR="port_mirror"
CONTAINER_SERVER="container_server"
CONTAINER_CLIENT="container_client"
CONTAINER_MIRROR="container_mirror"


## DO NOT MODIFY THE FOLLOWING PART, UNLESS YOU KNOW WHAT IT MEANS ##
echo_r () {
    [ $# -ne 1 ] && return 0
    echo -e "\033[31m$1\033[0m"
}
echo_g () {
    [ $# -ne 1 ] && return 0
    echo -e "\033[32m$1\033[0m"
}
echo_y () {
    [ $# -ne 1 ] && return 0
    echo -e "\033[33m$1\033[0m"
}
echo_b () {
    [ $# -ne 1 ] && return 0
    echo -e "\033[34m$1\033[0m"
}

get_port_uuid() {
    [ $# -ne 1 ] && echo_r "Wrong parameter number is given: $#" && exit 1
    local port_name=$1
    echo `ovs-vsctl get port "${port_name}" _uuid`

}

echo_g "Required: openvswitch, docker, ovs-docker, sar"

echo_g "Cleaning environment..."
echo_b "Cleaning the existing containers..."
sudo docker rm -f ${CONTAINER_SERVER} ${CONTAINER_CLIENT}
echo_b "Clearing the mirroring rules..."
ovs-vsctl clear Bridge ${OVS_BR} mirrors

echo_b "Installing ovs-docker into /usr/bin..."
install ovs-docker /usr/bin/

# Check requisites here...TBD
#[ ! -x ovs-docker ] && \
#    echo "Required ovs-docker script is not found" && \
#    echo "Download from https://github.com/openvswitch/ovs/raw/master/utilities/ovs-docker" && \
#    exit;

echo_g "Creating an ovs bridge ${OVS_BR}..."
sudo ovs-vsctl --may-exist add-br ${OVS_BR}

echo_g "Configuring internal port to 172.17.0.1/16..."
sudo ifconfig ${OVS_BR} 172.17.0.1/16

echo_g "Boot two raw containers without networking..."
cid1=`sudo docker run -d --net=none --privileged=true --name=${CONTAINER_SERVER} gdanii/iperf:latest /bin/sh -c "while true; do echo active; sleep 60; done"`
cid2=`sudo docker run -d --net=none --privileged=true --name=${CONTAINER_CLIENT} gdanii/iperf:latest /bin/sh -c "while true; do echo active; sleep 60; done"`
echo_b "The container id is $cid1, $cid2"

echo_g "Adding nic insides containers, and binding to the ovs bridge..."
sudo ovs-docker add-port ${OVS_BR} eth0 $cid1 172.17.0.2/16 172.17.0.1 ${PORT_SERVER}
sudo ovs-docker add-port ${OVS_BR} eth0 $cid2 172.17.0.3/16 172.17.0.1 ${PORT_CLIENT}

echo_g "Boot a raw containers for mirroring..."
cid3=`sudo docker run -d --net=none --privileged=true --name=${CONTAINER_MIRROR} gdanii/iperf:latest /bin/sh -c "while true; do echo active; sleep 60; done"`
echo_g "Creating a mirror port: ${PORT_MIRROR}..."
sudo ovs-docker add-port ${OVS_BR} eth0 $cid3 172.17.0.4/16 172.17.0.1 ${PORT_MIRROR}

### core capturing part ###
echo_g "Setting mirror rule..."
ovs-vsctl -- set Bridge ${OVS_BR} mirrors=@m \
    -- --id=@port_server get port ${PORT_SERVER}_l \
    -- --id=@port_client get port ${PORT_CLIENT}_l \
    -- --id=@port_mirror get port ${PORT_MIRROR}_l \
    -- --id=@m create Mirror name=mymirror select_src_port=@port_server select_dst_port=@port_server output-port=@port_mirror

ovs-vsctl list mirror mymirror
sleep 5

echo_g "Starting iperf server on 172.17.0.2..."
sudo docker exec $cid1 iperf -s &

sleep 1

sar -u 1 22 > stat_sending_mirroring.txt &

sleep 1

echo_g "Starting iperf client on 172.17.0.3 for 20 seconds..."
sudo docker exec $cid2 iperf -t 20 -c 172.17.0.2

echo_g "Removing the binding interfaces..."
sudo ovs-docker del-port ${OVS_BR} eth0 $cid1
sudo ovs-docker del-port ${OVS_BR} eth0 $cid2
sudo ovs-docker del-port ${OVS_BR} eth0 $cid3

echo_g "Killing the containers..."
sudo docker rm -f $cid1 $cid2 $cid3

echo_g "Clearing the mirroring rules..."
ovs-vsctl clear Bridge ${OVS_BR} mirrors

echo_g "Removing the ovs bridge ${OVS_BR}..."
sudo ovs-vsctl --if-exists del-br ${OVS_BR}

