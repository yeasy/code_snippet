#!/bin/sh
# This scirpt provides a safer & smarter way for 
# remote login, which will automatically authorize 
# the login without passwd input. It's under GNU license.
# Feel free to distribute or modify the code.:)
# Author: Baohua Yang@THU
# Updated: Aug 3, 2011
# Created: Mar 27, 2011
# Version: 0.11
# Usage: 
#  Download an run 'chmod a+x remoteAuth.sh'
#  Run 'remoteAuth.sh username remote_host_ip'
#  Enjoy!

# check parameters
if [ $# -ne 2 ]; then
    echo "[Usage]: $0 user remote_host_ip"
    exit
else
    echo "Starting authorizing..."
fi

username="$1"
remote_ip="$2"

#check public key file
pubkey="$HOME/.ssh/id_rsa.pub"
if [ -e $pubkey ]; then
    echo "Public key file $pubkey already exists, use it"
else
    echo "No public key file, generate one first"
    ssh-keygen -t rsa
fi

#scp public key file to remote machine
echo "Connecting to $remote_ip with username $username..."
echo "You may be asked to input remote passwd several times"
#scp $pubkey $username@$remote_ip:~/authorized_keys_tmp
#ssh $username@$remote_ip "cp -p authorized_keys_tmp .ssh/authorized_keys_tmp; rm authorized_keys_tmp; pushd .ssh; cat authorized_keys_tmp >> authorized_keys; rm authorized_keys_tmp"
cat $pubkey | ssh $username@$remote_ip 'cat >> ~/.ssh/authorized_keys'

