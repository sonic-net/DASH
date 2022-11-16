#!/bin/bash
# To be run inside saithrift-client container, assumes SAI repo portions exist under /SAI directory

ptf --test-dir functional --pypath /SAI/ptf --interface 0@veth1 --interface 1@veth3 saidashvnet_sanity $@
