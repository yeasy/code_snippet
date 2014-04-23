# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias v='vim -O'
alias ping='ping -n'
alias pa='ps aux|grep'
alias sinstall='sudo apt-fast install -y'
alias supdate='sudo apt-fast update; sudo apt-fast upgrade'
alias rm='/usr/local/bin/rm.sh'
alias sgw='ssh -X baohua@9.186.105.181'
alias sn='ssh -X root@9.186.105.54'
alias st='ssh baohua@server2.verkstad.net'
alias so='ssh -X baohua@9.186.105.154'
alias snfs='ssh -X root@9.186.105.78'
alias sx='ssh -X root@9.186.105.81'

# Openstack Aliases
alias novh='nova hypervisor-list'
alias novm='nova-manage service list'
alias vsh="sudo virsh list"
alias prof="vi ~/.bash_profile"
alias nmap="nmap -sT "
alias src="source ~/.bashrc"
alias lsof6='lsof -P -iTCP -sTCP:LISTEN | grep 66'
alias vsh="sudo virsh list"
alias ns="sudo ip netns exec "
alias ipt="sudo iptables --line-numbers -vnL"

# OVS Aliases
alias ovapd="sudo ovs-appctl bridge/dump-flows "
alias ovaps="sudo ovs-appctl fdb/show "
alias ovaf='sudo ovs-ofctl add-flow'
alias ovdpd=" sudo ovs-dpctl dump-flows "
alias ovdps='sudo ovs-dpctl show'
alias ovofd="sudo ovs-ofctl dump-flows"
alias ovofs="sudo ovs-ofctl show"
alias ovs='sudo ovs-vsctl show'
alias ovsd='sudo ovsdb-client dump'
alias logs="sudo journalctl -n 300 --no-pager"
alias ologs="tail -n 300 /var/log/openvswitch/ovs-vswitchd.log"
alias ovtun="sudo ovs-ofctl dump-flows br-tun"
alias ovint="sudo ovs-ofctl dump-flows br-int"
alias dfl="sudo ovs-ofctl -O OpenFlow13 del-flows "
alias ovls="sudo ovs-ofctl -O OpenFlow13  dump-flows br-int"
alias ofport=" sudo ovs-ofctl -O OpenFlow13 dump-ports br-int"
alias del=" sudo ovs-ofctl -O OpenFlow13 del-flows "
alias ovdelm=" sudo ovs-vsctl del-manager"
alias ovaddm=" sudo ovs-vsctl set-manager tcp:172.16.58.1:6640"
alias ovstart='sudo /usr/share/openvswitch/scripts/ovs-ctl start'
alias ovsm="ovs_mon.sh "
