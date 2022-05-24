SHELL = /bin/bash

PWD := $(shell pwd)

DOCKER_RUN := docker run \
	-it \
	--name simple_switch \
	-v $(PWD)/bmv2:/bmv2 \
	-v $(PWD)/behavioral-model:/bm-src \
	--network=host \
	--rm \
	bmv2-$(USER)

bmv2/sirius_pipeline.bmv2/sirius_pipeline.json: bmv2/*.p4
	$(DOCKER_RUN) p4c -b bmv2 bmv2/sirius_pipeline.p4 -o bmv2/sirius_pipeline.bmv2

clean:
	rm -rf bmv2/sirius_pipeline.bmv2

run-switch:
	$(DOCKER_RUN) sudo LD_LIBRARY_PATH=/usr/local/lib simple_switch --log-console --interface 0@veth0 --interface 1@veth2 /bmv2/sirius_pipeline.bmv2/sirius_pipeline.json

docker:
	docker build \
	    --no-cache \
	    -t bmv2-$(USER) \
	    --build-arg user=$(USER) \
	    --build-arg uid=$(shell id -u) \
	    --build-arg guid=$(shell id -g) \
	    --build-arg hostname=$(shell echo $$HOSTNAME) \
	    .

network:
	ip link add name veth0 type veth peer name veth1
	ip link set dev veth0 up
	ip link set dev veth1 up
	ip link set veth0 mtu 9500
	ip link set veth1 mtu 9500
	sysctl net.ipv6.conf.veth0.disable_ipv6=1
	sysctl net.ipv6.conf.veth1.disable_ipv6=1
	ip link add name veth2 type veth peer name veth3
	ip link set dev veth2 up
	ip link set dev veth3 up
	ip link set veth2 mtu 9500
	ip link set veth3 mtu 9500
	sysctl net.ipv6.conf.veth2.disable_ipv6=1
	sysctl net.ipv6.conf.veth3.disable_ipv6=1
