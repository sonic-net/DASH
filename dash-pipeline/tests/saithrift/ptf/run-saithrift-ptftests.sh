#!/bin/bash
# To be run inside saithrift-client container, assumes SAI repo portions exist under /SAI directory
sudo ptf --test-dir . --pypath /SAI/ptf \
	 --interface 0@veth1 --interface 1@veth3

