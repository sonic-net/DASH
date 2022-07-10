SHELL = /bin/bash

all:p4 sai sai-thrift-server test

PWD := $(shell pwd)

# Default Docker images, override from env var
# https://hub.docker.com/r/p4lang/p4c
# p4lang version 971MB - works:
#DOCKER_P4C_BMV2_IMG ?=p4lang/p4c:stable

# Slimmed-down version bmv2 backend only 632MB - works:
DOCKER_P4C_BMV2_IMG ?=chrissommers/dash-p4c-bmv2:220701

# Builds sai-P4rt clients to run inside bmvs process
DOCKER_BMV2_BLDR_IMG ?=chrissommers/dash-bmv2-bldr:220630

# Runs bmv2 process - consider slimmer if don't need sai/p4rt clients inside
DOCKER_BMV2_RUN_IMG ?=$(DOCKER_BMV2_BLDR_IMG)

# Compiles sai headers, libsai, saithrift client-server
DOCKER_SAITHRIFT_BLDR_IMG ?=chrissommers/dash-saithrift-bldr:220708

# Compiles sai headers, libsai, saithrift client-server
DOCKER_GRPC_IMG ?=chrissommers/dash-grpc:1.43.2

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


.PHONY:clean
clean: kill-switch p4-clean sai-clean test-clean network-clean undeploy-ixiac
	rm -rf bmv2/dash_pipeline.bmv2
	make -C tests/vnet_out clean

######################################
# P4 Source code compile TARGETS
######################################

P4_ARTIFACTS=bmv2/dash_pipeline.bmv2/dash_pipeline.json bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt

p4: bmv2/dash_pipeline.bmv2/dash_pipeline.json

.PHONY:p4-clean
p4-clean:
	-rm -rf $(P4_ARTIFACTS)

P4_SRC=$(wildcard bmv2/*.p4)
P4_MAIN=bmv2/dash_pipeline.p4
P4_OUTDIR=bmv2/dash_pipeline.bmv2
# Compile P4 into bmv2 .json fle and P4info for SAI header autogeneration
$(P4_ARTIFACTS): $(P4_SRC)
	@echo "Compile P4 program $(P4_MAIN) ..."
	mkdir -p $(P4_OUTDIR) && \
	docker run \
	--rm \
	--name dash-p4c-$(USER) \
	$(DOCKER_FLAGS) \
	-v $(PWD)/bmv2:/bmv2 \
	-w / \
	$(DOCKER_P4C_BMV2_IMG) p4c \
	    $(P4_MAIN) \
		-b bmv2 \
		-o $(P4_OUTDIR) \
	    --p4runtime-files $(P4_OUTDIR)/dash_pipeline_p4rt.json,$(P4_OUTDIR)/dash_pipeline_p4rt.txt

######################################
# DASH SAI HEADER & libsai.so TARGETS
######################################


# Note we have to mount main DASH dir to allow container to "see" the parent Git repo for the SAI submodule
DOCKER_RUN_SAITHRIFT =\
	docker run \
	--rm \
	--name dash-saithrift-bldr-$(USER) \
	-v $(PWD)/..:/dash -w /dash/dash-pipeline/SAI/saithrift \
	$(DOCKER_SAITHRIFT_BLDR_IMG) \

# TODO - create separate rules for headers, libsai.so
.PHONY:sai

sai:sai-headers sai-meta libsai

sai-headers: p4 | SAI/SAI 
	@echo "Generate SAI library headers and implementation..."
	mkdir -p SAI/lib
	$(DOCKER_RUN) \
		$(DOCKER_FLAGS) \
		--name build_sai-$(USER) \
		-w /SAI $(DOCKER_SAITHRIFT_BLDR_IMG) \
	    ./generate_dash_api.sh
	# Fixup perms from generate_dash_api using sudo to call python,so subsequent scripts can access
	sudo chmod -R a+rw $(PWD)/SAI/SAI
	# sudo chown -R $(USER) .

sai-meta:
	@echo "Generate SAI metadata..."
	# ./add_safe_git_dirs.sh
	docker run \
		$(DOCKER_FLAGS) \
		--rm \
		--name dash-saithrift-bldr-$(USER) \
		-v $(PWD)/..:/dash -w /dash \
		$(DOCKER_SAITHRIFT_BLDR_IMG) \
	    ./dash-pipeline/make_meta_wrapper.sh

# TODO - add SAI header dependencies
libsai:
	@echo "build libsai.so..."
	$(DOCKER_RUN) \
		$(DOCKER_FLAGS) \
		-w /SAI/lib \
		--name build_libsai-$(USER) \
		$(DOCKER_BMV2_BLDR_IMG) \
	    make

libsai-clean:
	-rm -rf SAI/lib/libsai.so

.PHONY:sai-clean
sai-clean: SAI/SAI libsai-clean
	@echo "Restoring SAI subdirectories to baseline..."
	rm -rf SAI/SAI/inc SAI/SAI/experimental SAI/SAI/meta
	cd SAI/SAI && git checkout -- inc experimental meta

######################################
# P4 Behavioral-model (switch) TARGETS
######################################

.PHONY:run-switch
run-switch: network
	$(DOCKER_RUN) \
		--name simple_switch-$(USER) \
		-u root \
		-v $(PWD)/bmv2/dash_pipeline.bmv2/dash_pipeline.json:/etc/dash/dash_pipeline.json \
		-v $(PWD)/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt:/etc/dash/dash_pipeline_p4rt.txt \
		$(DOCKER_BMV2_RUN_IMG) \
		env LD_LIBRARY_PATH=/usr/local/lib \
		simple_switch_grpc \
		--interface 0@veth0 \
		--interface 1@veth2 \
		--log-console \
		--no-p4

kill-switch:
	-docker kill simple_switch-$(USER)


###############################
# SAI-THRIFT SERVER TARGETS
###############################

sai-thrift-server:
	$(DOCKER_RUN_SAITHRIFT) \
	    make $@

run-sai-thrift-server:
	docker run \
	--rm \
	-it \
	--net=host \
	--name dash-saithrift-server-$(USER) \
	-v $(PWD)/bmv2/dash_pipeline.bmv2/dash_pipeline.json:/etc/dash/dash_pipeline.json \
	-v $(PWD)/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt:/etc/dash/dash_pipeline_p4rt.txt \
	-v $(PWD)/SAI:/SAI -w /SAI/rpc \
	-e LD_LIBRARY_PATH=/SAI/lib:/usr/local/lib \
	$(DOCKER_SAITHRIFT_BLDR_IMG) \
	./usr/sbin/saiserver

kill-sai-thrift-server:
	-docker kill dash-saithrift-server-$(USER)

sai-thrift-server-bash:
	docker run \
	--rm \
	-it \
	--name dash-saithrift-bldr-$(USER) \
	-v $(PWD)/..:/dash -w /dash/dash-pipeline/SAI/saithrift \
	$(DOCKER_SAITHRIFT_BLDR_IMG) \
	/bin/bash

sai-thrift-server-clean:
	$(DOCKER_RUN_SAITHRIFT) \
	    make $@



###############################
# SAI TEST TARGETS
###############################

.PHONY:test sai-test
test:sai-test

test-clean:
	make -C tests clean


.PHONY:sai-test
sai-test:SAI/SAI SAI/lib/libsai.so
	$(DOCKER_RUN) \
	    --name dash-build-test-$(USER) \
		-w /tests  $(DOCKER_BMV2_BLDR_IMG) \
	    make

timeout?=5
run-all-tests:run-test run-ixiac-test

.PHONY:run-test
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

# Make sure we have executable
tests/init_switch/init_switch:sai-test

.PHONY:init-switch
init-switch:
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
	docker exec -w /tests/init_switch simple_switch-$(USER) ./init_switch

###############################
# DOCKER BUILD/PUBLISH TARGETS
###############################

docker-bmv2-bldr:
	docker build \
		-f dockerfiles/Dockerfile.bmv2-bldr \
	    -t $(DOCKER_BMV2_BLDR_IMG) \
	    --build-arg user=$(USER) \
	    --build-arg uid=$(shell id -u) \
	    --build-arg guid=$(shell id -g) \
	    --build-arg hostname=$(shell echo $$HOSTNAME) \
	    --build-arg available_processors=$(shell nproc) \
	    dockerfiles

docker-publish-bmv2-bldr:
	echo "TO DO when we have a proper repository"

docker-pull-bmv2-bldr:
	docker pull $(DOCKER_BMV2_BLDR_IMG)
###############################
docker-saithrift-bldr:
	docker build \
		-f dockerfiles/Dockerfile.saithrift \
	    -t $(DOCKER_SAITHRIFT_BLDR_IMG) \
	    --build-arg user=$(USER) \
	    --build-arg uid=$(shell id -u) \
	    --build-arg guid=$(shell id -g) \
	    --build-arg hostname=$(shell echo $$HOSTNAME) \
	    --build-arg available_processors=$(shell nproc) \
		dockerfiles
docker-publish-saithrift-bldr:
	echo "TO DO when we have a proper repository"

docker-pull-saithrift-bldr:
	docker pull $(DOCKER_SAITHRIFT_BLDR_IMG)

###############################

docker-dash-p4c:
	docker build \
		-f dockerfiles/Dockerfile.p4c-bmv2 \
	    -t $(DOCKER_P4C_BMV2_IMG) \
	    --build-arg user=$(USER) \
	    --build-arg uid=$(shell id -u) \
	    --build-arg guid=$(shell id -g) \
	    --build-arg hostname=$(shell echo $$HOSTNAME) \
	    --build-arg available_processors=$(shell nproc) \
		dockerfiles

docker-pull-dash-p4c:
	docker pull $(DOCKER_P4C_BMV2_IMG)

docker-publish-dash-p4c:
	echo "TO DO when we have a proper repository"
###############################

docker-dash-grpc:
	docker build \
		-f dockerfiles/Dockerfile.grpc1.43.2 \
	    -t $(DOCKER_GRPC_IMG) \
	    --build-arg user=$(USER) \
	    --build-arg uid=$(shell id -u) \
	    --build-arg guid=$(shell id -g) \
	    --build-arg hostname=$(shell echo $$HOSTNAME) \
	    --build-arg available_processors=$(shell nproc) \
		dockerfiles

docker-pull-dash-grpc:
	docker pull $(DOCKER_GRPC_IMG)

docker-publish-dash-grpc:
	echo "TO DO when we have a proper repository"

###############################
# BMV2-PKTGEN NETWORKING TARGETS
###############################

network:veth0 veth2

veth0: /sys/class/net/veth0
/sys/class/net/veth0:

	sudo ip link add name veth0 type veth peer name veth1
	sudo ip link set dev veth0 up
	sudo ip link set dev veth1 up
	sudo ip link set veth0 mtu 9500
	sudo ip link set veth1 mtu 9500
	sudo sysctl net.ipv6.conf.veth0.disable_ipv6=1
	#https://superuser.com/questions/33196/how-to-disable-autoconfiguration-on-ipv6-in-linux
	sudo sysctl net.ipv6.conf.veth0.autoconf=0
	sudo sysctl net.ipv6.conf.veth0.accept_ra=0
	sudo sysctl net.ipv6.conf.veth0.accept_ra_pinfo=0
	sudo sysctl net.ipv6.conf.veth0.router_solicitations=0
	sudo sysctl net.ipv6.conf.veth1.disable_ipv6=1
	sudo sysctl net.ipv6.conf.veth1.autoconf=0
	sudo sysctl net.ipv6.conf.veth1.accept_ra=0
	sudo sysctl net.ipv6.conf.veth1.accept_ra_pinfo=0
	sudo sysctl net.ipv6.conf.veth1.router_solicitations=0

veth2: /sys/class/net/veth2
/sys/class/net/veth2:
	sudo ip link add name veth2 type veth peer name veth3
	sudo ip link set dev veth2 up
	sudo ip link set dev veth3 up
	sudo ip link set veth2 mtu 9500
	sudo ip link set veth3 mtu 9500
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

network-clean:
	# Note, deleting one member (e.g. veth0) deletes its peer (e.g. veth1)
	-sudo ip link delete dev veth0
	-sudo ip link delete dev veth2

###############################
# IXIA-C TARGETS
###############################

run-ixiac-test: ixiac-prereq init-switch
	python3 -m pytest ../test/test-cases/bmv2_model/ -s

ixiac-prereq: install-python-modules deploy-ixiac

install-python-modules:
	python3 -m pip install -r ../test/requirements.txt

deploy-ixiac:
	cd ../test/third-party/traffic_gen && ./deploy_ixiac.sh

undeploy-ixiac:
	cd ../test/third-party/traffic_gen && ./undeploy_ixiac.sh


###############################
# ENVIRONMENT SETUP TARGETS
###############################

install-docker-compose:
	sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$$(uname -s)-$$(uname -m)" -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
