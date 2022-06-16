SHELL = /bin/bash

PWD := $(shell pwd)

# Default Docker image, override from env var
DOCKER_IMG ?=chrissommers/dash-bmv2:latest

# Set to -d for CI mode
DOCKER_FLAGS ?=-it

# Should override --name in make targets
DOCKER_RUN := docker run \
	-v $(PWD)/bmv2:/bmv2 \
	-v $(PWD)/SAI:/SAI \
	-v $(PWD)/tests:/tests \
	-v $(PWD)/..:/dash \
	--network=host \
	--rm \
	$(DOCKER_FLAGS)

#shorthand:
p4:bmv2/sirius_pipeline.bmv2/sirius_pipeline.json

bmv2/sirius_pipeline.bmv2/sirius_pipeline.json:
	$(DOCKER_RUN) \
	--name p4c \
	$(DOCKER_IMG) p4c \
	    -b \
	    bmv2 \
	    bmv2/sirius_pipeline.p4 \
	    -o bmv2/sirius_pipeline.bmv2 \
	    --p4runtime-files bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.json,bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.txt

clean:
	rm -rf bmv2/sirius_pipeline.bmv2
	rm -rf SAI/lib
	make -C tests/vnet_out clean

dash-shell:
	$(DOCKER_RUN) \
	    --name dashshell-$(USER) \
		 $(DOCKER_IMG) \
	    bash

run-switch:
	$(DOCKER_RUN) \
	    --name simple_switch-$(USER) \
	    -v $(PWD)/bmv2/sirius_pipeline.bmv2/sirius_pipeline.json:/etc/dash/sirius_pipeline.json \
	    -v $(PWD)/bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.txt:/etc/dash/sirius_pipeline_p4rt.txt \
	    $(DOCKER_IMG) \
	    sudo \
	    env LD_LIBRARY_PATH=/usr/local/lib \
	    simple_switch_grpc \
	    --interface 0@veth0 \
	    --interface 1@veth2 \
	    --log-console \
	    --no-p4

sai:
	# Generate SAI library headers and implementation
	$(DOCKER_RUN) \
		--name build_sai-$(USER) \
		-w /dash $(DOCKER_IMG) \
	    sirius-pipeline/SAI/generate_dash_api.sh
	# build libsai.so
	$(DOCKER_RUN) -w /SAI/lib $(DOCKER_IMG) \
	    make

test:
	$(DOCKER_RUN) \
	    --name build-test-$(USER) \
		-w /tests/vnet_out  $(DOCKER_IMG) \
	    make

timeout?=5
run-test:
	# Ensure P4Runtime server is listening
	t=$(timeout); \
	while [ $${t} -ge 1 ]; do \
		if sudo lsof -i:9559 | grep LISTEN >/dev/null; then \
			break; \
		else \
			sleep 1; \
			t=`expr $$t - 1`; \
		fi; \
	done; \
	docker exec $(DOCKER_FLAGS) -w /tests/vnet_out simple_switch-$(USER) ./vnet_out

docker:
	docker build \
	    -t $(DOCKER_IMG) \
	    --build-arg user=$(USER) \
	    --build-arg uid=$(shell id -u) \
	    --build-arg guid=$(shell id -g) \
	    --build-arg hostname=$(shell echo $$HOSTNAME) \
	    --build-arg available_processors=$(shell nproc) \
	    .

docker-publish:
	echo "TO DO when we have a proper repository"

docker-pull:
	docker pull $(DOCKER_IMG)

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
	python3 -m pytest ../test/test-cases/bmv2_model/ -s

ixiac-prereq: install-python-modules deploy-ixiac

install-python-modules:
	python3 -m pip install -r ../test/requirements.txt

deploy-ixiac:
	cd ../test/third-party/traffic_gen && ./deploy_ixiac.sh

install-docker-compose:
	sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$$(uname -s)-$$(uname -m)" -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose