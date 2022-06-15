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

timeout?=5
run-test:
	t=$(timeout); \
	while [ $${t} -ge 1 ]; do \
		if sudo lsof -i:9559 | grep LISTEN >/dev/null; then \
			break; \
		else \
			sleep 1; \
			t=`expr $$t - 1`; \
		fi; \
	done; \
	docker exec -w /tests/vnet_out simple_switch-$(USER) ./vnet_out

docker:
	docker build \
	    -t bmv2-$(USER) \
	    --build-arg user=$(USER) \
	    --build-arg uid=$(shell id -u) \
	    --build-arg guid=$(shell id -g) \
	    --build-arg hostname=$(shell echo $$HOSTNAME) \
	    --build-arg available_processors=$(shell nproc) \
	    .

network:
	sudo ip link add name veth0 type veth peer name veth1
	sudo ip link set dev veth0 up
	sudo ip link set dev veth1 up
	sudo ip link set veth0 mtu 9500
	sudo ip link set veth1 mtu 9500
	sudo sysctl net.ipv6.conf.veth0.disable_ipv6=1
	sudo sysctl net.ipv6.conf.veth1.disable_ipv6=1
	sudo ip link add name veth2 type veth peer name veth3
	sudo ip link set dev veth2 up
	sudo ip link set dev veth3 up
	sudo ip link set veth2 mtu 9500
	sudo ip link set veth3 mtu 9500
	sudo sysctl net.ipv6.conf.veth2.disable_ipv6=1
	sudo sysctl net.ipv6.conf.veth3.disable_ipv6=1

run-ixiac-test: ixiac-prereq
	python3 -m pytest ../test/test-cases/sirius/hello_world.py

ixiac-prereq: install-python-modules deploy-ixiac

install-python-modules:
	python3 -m pip install -r ../test/requirements.txt

deploy-ixiac:
	cd ../test/third-party/traffic_gen && ./deploy_ixiac.sh