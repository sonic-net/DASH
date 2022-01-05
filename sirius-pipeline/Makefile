SHELL = /bin/bash

PWD := $(shell pwd)

DOCKER_RUN := docker run \
	-it \
	--name simple_switch \
	-v $(PWD)/bmv2:/bmv2 \
	-v $(PWD)/behavioral-model:/bm-src \
	--network=host \
	--rm \
	bmv2

DOCKER_RUN_BASE := docker run \
	-it \
	--name simple_switch \
	-v $(PWD)/bmv2:/bmv2 \
	-v $(PWD)/behavioral-model:/bm-src \
	--network=host \
	--rm \
	bmv2-base

bmv2/sirius_pipeline.bmv2/sirius_pipeline.json:
	$(DOCKER_RUN) p4c -b bmv2 bmv2/sirius_pipeline.p4 -o bmv2/sirius_pipeline.bmv2

clean:
	rm -rf bmv2/sirius_pipeline.bmv2

run_switch:
	$(DOCKER_RUN) simple_switch --log-console --interface 0@veth0 --interface 1@veth2 /bmv2/sirius_pipeline.bmv2/sirius_pipeline.json

docker-base:
	docker build -t bmv2-base -f Dockerfile.base bmv2/

bm:
	$(DOCKER_RUN_BASE) bash -c 'cd /bm-src && ./autogen.sh && ./configure && make'

docker:
	docker build -t bmv2 -f Dockerfile.run .

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
