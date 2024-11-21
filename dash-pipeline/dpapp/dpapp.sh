#!/bin/bash
set -m

[ -d /var/log/vpp ] || mkdir -p /var/log/vpp

sysctl vm.nr_hugepages=32

/usr/bin/vpp -c ${1:-/etc/vpp/startup.conf} &
sleep 5

# Create a host interface which connects p4 bmv2 simple_switch
HOST_INTERFACE=${HOST_INTERFACE:-veth5}
HOST_INTERFACE_MAC=`cat /sys/class/net/$HOST_INTERFACE/address`
vppctl create host-interface name $HOST_INTERFACE hw-addr $HOST_INTERFACE_MAC
vppctl set interface state host-$HOST_INTERFACE up

# Move vpp to foreground
fg %1
