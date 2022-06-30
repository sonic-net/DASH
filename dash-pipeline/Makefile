SHELL = /bin/bash

all:p4 sai test

PWD := $(shell pwd)

# Default Docker images, override from env var
DOCKER_BMV2_IMG ?=chrissommers/dash-bmv2:pr127-220623
DOCKER_P4C_IMG ?=p4lang/p4c:stable

# Set differently in CI scripts as needed, e.g. run switch container in -d mode
DOCKER_FLAGS ?=-it

# Should override --name in make targets
DOCKER_RUN := docker run \
	-v $(PWD)/bmv2:/bmv2 \
	-v $(PWD)/SAI:/SAI \
	-v $(PWD)/tests:/tests \
	--network=host \
	--rm \
	$(DOCKER_FLAGS)

SAI/SAI:
	@echo "Initializing SAI submodule..."
	git submodule update --init

P4_ARTIFACTS=bmv2/dash_pipeline.bmv2/dash_pipeline.json bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt

p4: bmv2/dash_pipeline.bmv2/dash_pipeline.json

.PHONY:p4-clean
p4-clean:
	-sudo rm -rf $(P4_ARTIFACTS)

P4_SRC=bmv2/dash_pipeline.p4
$(P4_ARTIFACTS):
	@echo "Compile P4 program $(P4_SRC) ..."
	docker run \
	--rm --name p4c \
	$(DOCKER_FLAGS) \
	-v $(PWD)/bmv2:/bmv2 \
	-w / \
	$(DOCKER_P4C_IMG) p4c \
	    -b \
	    bmv2 \
	    $(P4_SRC) \
	    -o bmv2/dash_pipeline.bmv2 \
	    --p4runtime-files bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.json,bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt

.PHONY:clean
clean: kill-switch p4-clean sai-clean test-clean network-clean undeploy-ixiac
	sudo rm -rf bmv2/dash_pipeline.bmv2
	sudo make -C tests/vnet_out clean

.PHONY:dash-shell
dash-shell:
	$(DOCKER_RUN) \
	    --name dashshell-$(USER) \
		 $(DOCKER_BMV2_IMG) \
	    bash

.PHONY:run-switch
run-switch:
	$(DOCKER_RUN) \
	    --name simple_switch-$(USER) \
	    -v $(PWD)/bmv2/dash_pipeline.bmv2/dash_pipeline.json:/etc/dash/dash_pipeline.json \
	    -v $(PWD)/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt:/etc/dash/dash_pipeline_p4rt.txt \
	    $(DOCKER_BMV2_IMG) \
	    sudo \
	    env LD_LIBRARY_PATH=/usr/local/lib \
	    simple_switch_grpc \
	    --interface 0@veth0 \
	    --interface 1@veth2 \
	    --log-console \
	    --no-p4

kill-switch:
	-docker kill simple_switch-$(USER)

# TODO - create separate rules for headers, libsai.so
.PHONY:sai
sai: p4 | SAI/SAI 
	@echo "Generate SAI library headers and implementation..."
	$(DOCKER_RUN) \
		--name build_sai-$(USER) \
		-w /SAI $(DOCKER_BMV2_IMG) \
	    ./generate_dash_api.sh
	@echo "build libsai.so..."
	$(DOCKER_RUN) -w /SAI/lib $(DOCKER_BMV2_IMG) \
	    make

.PHONY:sai-clean
sai-clean: SAI/SAI 
	@echo "Restoring SAI subdirectories to baseline..."
	rm -rf SAI/SAI/inc SAI/SAI/experimental SAI/SAI/meta
	cd SAI/SAI && git checkout -- inc experimental meta
	sudo rm -rf SAI/lib

.PHONY:test sai-test
test:sai-test

test-clean:
	sudo make -C tests/vnet_out clean


#TODO - use libsai.so, headers as dep
sai-test:SAI/SAI
	$(DOCKER_RUN) \
	    --name build-test-$(USER) \
		-w /tests/vnet_out  $(DOCKER_BMV2_IMG) \
	    make

timeout?=5
run-all-tests:run-test run-ixiac-test

run-test:run-sai-test
run-sai-test:
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
	docker exec -w /tests/vnet_out simple_switch-$(USER) ./vnet_out

docker-bmv2:
	docker build \
	    -t $(DOCKER_BMV2_IMG) \
	    --build-arg user=$(USER) \
	    --build-arg uid=$(shell id -u) \
	    --build-arg guid=$(shell id -g) \
	    --build-arg hostname=$(shell echo $$HOSTNAME) \
	    --build-arg available_processors=$(shell nproc) \
	    .

docker-publish:
	echo "TO DO when we have a proper repository"

docker-pull-bmv2:
	docker pull $(DOCKER_BMV2_IMG)

docker-pull-p4c:
	docker pull $(DOCKER_P4C_IMG)

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

network-clean:
	# Note, deleting one member (e.g. veth0) deletes its peer (e.g. veth1)
	-sudo ip link delete dev veth0
	-sudo ip link delete dev veth2

run-ixiac-test: ixiac-prereq
	python3 -m pytest ../test/test-cases/bmv2_model/ -s

ixiac-prereq: install-python-modules deploy-ixiac

install-python-modules:
	python3 -m pip install -r ../test/requirements.txt

deploy-ixiac:
	cd ../test/third-party/traffic_gen && ./deploy_ixiac.sh

undeploy-ixiac:
	cd ../test/third-party/traffic_gen && ./undeploy_ixiac.sh

install-docker-compose:
	sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$$(uname -s)-$$(uname -m)" -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
