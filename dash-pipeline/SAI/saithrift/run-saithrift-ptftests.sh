#!/bin/bash
sudo ptf --test-dir ptf/ --pypath ${PWD}/../../SAI/ptf \
	 --interface 0@veth1 --interface 1@veth3