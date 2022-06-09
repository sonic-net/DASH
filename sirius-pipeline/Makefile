SHELL = /bin/bash

PWD := $(shell pwd)

DOCKER_RUN := docker run \
	--name simple_switch \
	-v $(PWD)/bmv2:/bmv2 \
	-v $(PWD)/SAI:/SAI \
	-v $(PWD)/tests:/tests \
	--network=host \
	--rm

bmv2/sirius_pipeline.bmv2/sirius_pipeline.json:
	$(DOCKER_RUN) bmv2-$(USER) p4c \
	    -b \
	    bmv2 \
	    bmv2/sirius_pipeline.p4 \
	    -o bmv2/sirius_pipeline.bmv2 \
	    --p4runtime-files bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.json,bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.txt

clean:
	rm -rf bmv2/sirius_pipeline.bmv2
	rm -rf SAI/SAI
	rm -rf SAI/lib
	make -C tests/vnet_out clean

run-switch:
	$(DOCKER_RUN) \
		-d \
	    -v $(PWD)/bmv2/sirius_pipeline.bmv2/sirius_pipeline.json:/etc/dash/sirius_pipeline.json \
	    -v $(PWD)/bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.txt:/etc/dash/sirius_pipeline_p4rt.txt \
	    --name simple_switch-$(USER) \
	    bmv2-$(USER) \
	    sudo \
	    env LD_LIBRARY_PATH=/usr/local/lib \
	    simple_switch_grpc \
	    --interface 0@veth0 \
	    --interface 1@veth2 \
	    --log-console \
	    --no-p4

sai:
	$(DOCKER_RUN) -w /SAI bmv2-$(USER) \
	    ./generate_dash_api.sh
	$(DOCKER_RUN) -w /SAI/lib bmv2-$(USER) \
	    make

test:
	$(DOCKER_RUN) -w /tests/vnet_out bmv2-$(USER) \
	    make

run-test:
	docker exec -it -w /tests/vnet_out simple_switch-$(USER) ./vnet_out

docker:
	docker build \
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
