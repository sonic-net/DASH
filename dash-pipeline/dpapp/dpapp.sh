#!/bin/bash

[ -d /var/log/vpp ] || mkdir -p /var/log/vpp

sysctl vm.nr_hugepages=512
sysctl vm.max_map_count=1548

/usr/bin/vpp -c ${1:-/etc/vpp/startup.conf} &
sleep 3

# Create a host interface which connects p4 bmv2 simple_switch
HOST_INTERFACE=${HOST_INTERFACE:-veth5}
vppctl create host-interface name $HOST_INTERFACE
vppctl set interface mac address host-$HOST_INTERFACE 02:fe:23:f0:e4:13
vppctl set interface state host-$HOST_INTERFACE up
vppctl set interface promiscuous on host-$HOST_INTERFACE
vppctl
