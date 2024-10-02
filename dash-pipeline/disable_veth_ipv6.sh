#!/bin/bash
echo "Disable IPv6 to suppress Linux control plane noise"
sudo sysctl net.ipv6.conf.veth0.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth0.autoconf=0
sudo sysctl net.ipv6.conf.veth0.accept_ra=0
sudo sysctl net.ipv6.conf.veth0.accept_ra_pinfo=0
sudo sysctl net.ipv6.conf.veth0.router_solicitations=0
sudo sysctl net.ipv6.conf.veth1.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth1.autoconf=0
sudo sysctl net.ipv6.conf.veth1.accept_ra=0
sudo sysctl net.ipv6.conf.veth1.accept_ra_pinfo=0
sudo sysctl net.ipv6.conf.veth1.router_solicitations=0
sudo sysctl net.ipv6.conf.veth2.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth2.autoconf=0
sudo sysctl net.ipv6.conf.veth2.accept_ra=0
sudo sysctl net.ipv6.conf.veth2.accept_ra_pinfo=0
sudo sysctl net.ipv6.conf.veth2.router_solicitations=0
sudo sysctl net.ipv6.conf.veth3.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth3.autoconf=0
sudo sysctl net.ipv6.conf.veth3.accept_ra=0
sudo sysctl net.ipv6.conf.veth3.accept_ra_pinfo=0
sudo sysctl net.ipv6.conf.veth3.router_solicitations=0

if [ $DPAPP_LINK ]; then
sudo sysctl net.ipv6.conf.$DPAPP_LINK.autoconf=0
sudo sysctl net.ipv6.conf.$DPAPP_LINK.accept_ra=0
sudo sysctl net.ipv6.conf.$DPAPP_LINK.accept_ra_pinfo=0
sudo sysctl net.ipv6.conf.$DPAPP_LINK.router_solicitations=0
fi
if [ $DPAPP_LINK_PEER ]; then
sudo sysctl net.ipv6.conf.$DPAPP_LINK_PEER.disable_ipv6=1
sudo sysctl net.ipv6.conf.$DPAPP_LINK_PEER.autoconf=0
sudo sysctl net.ipv6.conf.$DPAPP_LINK_PEER.accept_ra=0
sudo sysctl net.ipv6.conf.$DPAPP_LINK_PEER.accept_ra_pinfo=0
sudo sysctl net.ipv6.conf.$DPAPP_LINK_PEER.router_solicitations=0
fi
