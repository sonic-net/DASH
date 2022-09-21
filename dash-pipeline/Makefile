SHELL = /bin/bash

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

# "All" type targets for convenience
all:p4 sai saithrift-server docker-saithrift-client test

run-all-tests:run-libsai-test run-saithrift-client-tests
run-saithrift-client-tests: run-saithrift-ptftests run-saithrift-pytests
run-saithrift-client-dev-tests: run-saithrift-dev-ptftests run-saithrift-dev-pytests

.PHONY:clean
clean: kill-all p4-clean sai-clean test-clean network-clean saithrift-server-clean
	rm -rf $(P4_OUTDIR)

kill-all: kill-saithrift-server kill-switch undeploy-ixiac

PWD := $(realpath $(mkfile_dir))
DASH_USER ?=dashuser
DASH_GROUP ?=dashusers
DASH_UID ?=4321
DASH_GUID?=4321
DASH_HOST?=dash

# Default Docker images, override from env var

# Needed Libraries only
DOCKER_GRPC_IMG ?=chrissommers/dash-grpc:1.43.2

# Slimmed-down version bmv2 backend only 632MB:
DOCKER_P4C_BMV2_IMG ?=chrissommers/dash-p4c-bmv2:220825

# Builds SAI-P4RT clients to run inside bmv2 process
DOCKER_BMV2_BLDR_IMG ?=chrissommers/dash-bmv2-bldr:220819

# Runs bmv2 process - consider slimmer if don't need sai/p4rt clients inside
DOCKER_BMV2_RUN_IMG ?=$(DOCKER_BMV2_BLDR_IMG)

# Compiles sai headers, libsai, saithrift server & client/server libs
DOCKER_SAITHRIFT_BLDR_IMG ?=chrissommers/dash-saithrift-bldr:220819

# Base image with test frameworks, DASH client libs not installed
DOCKER_SAITHRIFT_CLIENT_BLDR_IMG ?=chrissommers/dash-saithrift-client-bldr:220819

# Client image built locally with saithrift client libs + PTF & Pytest frameworks
# TODO: consider some other tagging scheme
DOCKER_SAITHRIFT_CLIENT_IMG ?= local/dash-saithrift-client:latest

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

SAI/SAI: sai-submodule

sai-submodule:
	@echo "Initializing SAI submodule..."
	git submodule update --init
	@echo "Initializing SAI submodule..."
	cd SAI/SAI/test && git submodule update --init ptf


######################################
# P4 Source code compile TARGETS
######################################

P4_SRC=$(wildcard bmv2/*.p4)
P4_MAIN=bmv2/dash_pipeline.p4
P4_OUTDIR=bmv2/dash_pipeline.bmv2

P4_ARTIFACTS=$(P4_OUTDIR)/dash_pipeline.json $(P4_OUTDIR)/dash_pipeline_p4rt.txt

p4: $(P4_OUTDIR)/dash_pipeline.json

.PHONY:p4-clean
p4-clean:
	-rm -rf $(P4_OUTDIR)
# Compile P4 into bmv2 .json fle and P4info for SAI header autogeneration
$(P4_ARTIFACTS): $(P4_SRC)
	@echo "Compile P4 program $(P4_MAIN) ..."
	mkdir -p $(P4_OUTDIR) && \
	chmod o+w $(P4_OUTDIR) && \
	docker run \
	--rm \
	--name dash-p4c-$(USER) \
	-u $(DASH_USER) \
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

SAIRPC_VENDOR_EXTRA_LIBS?=""
# Note we have to mount main DASH dir to allow container to "see" the parent Git repo for the SAI submodule
DOCKER_RUN_SAITHRIFT_BLDR =\
	docker run \
	$(DOCKER_FLAGS) \
	--rm \
	--name dash-saithrift-bldr-$(USER) \
	-v $(PWD)/..:/dash -w /dash/dash-pipeline/SAI/saithrift \
	-e SAIRPC_VENDOR_EXTRA_LIBS=$(SAIRPC_VENDOR_EXTRA_LIBS) \
	$(DOCKER_SAITHRIFT_BLDR_IMG) \

# TODO - create separate rules for headers, libsai.so
.PHONY:sai

sai: sai-clean sai-headers sai-meta libsai

sai-headers: p4 | SAI/SAI 
	@echo "Generate SAI library headers and implementation..."
	mkdir -p SAI/lib && chmod -R o+w SAI && \
	$(DOCKER_RUN) \
		$(DOCKER_FLAGS) \
		--name build_sai-$(USER) \
		-w /SAI $(DOCKER_SAITHRIFT_BLDR_IMG) \
	    ./generate_dash_api.sh

sai-meta: 
	@echo "Generate SAI metadata..."
	# hack - remove scripts which cause Git ownership failures in CI pipelines
	# We don't need them, they're to check that SAI headers didn't experience enum changes etc.
	sed -ie '/checkenumlock.sh/d' SAI/SAI/meta/Makefile
	sed -ie '/checkancestry.sh/d' SAI/SAI/meta/Makefile
	docker run \
		$(DOCKER_FLAGS) \
		--rm \
		--name dash-saithrift-bldr-$(USER) \
		-v $(PWD)/..:/dash -w /dash/dash-pipeline/SAI/SAI/meta \
		$(DOCKER_SAITHRIFT_BLDR_IMG) \
	    make

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
	-rm -rf SAI/lib/*

.PHONY:sai-clean
sai-clean: SAI/SAI libsai-clean saithrift-server-clean
	@echo "Restoring SAI subdirectories to baseline..."
	rm -rf SAI/SAI/inc SAI/SAI/experimental SAI/SAI/meta
	cd SAI/SAI && git checkout -- inc experimental meta


# Run to recreate same environment as building saithrift client & server
run-saithrift-bldr-bash:
	$(DOCKER_RUN_SAITHRIFT_BLDR) \
	    /bin/bash

######################################
# P4 Behavioral-model (switch) TARGETS
######################################

.PHONY:run-switch
run-switch: network
	$(DOCKER_RUN) \
		--name simple_switch-$(USER) \
		-u root \
		-v $(PWD)/$(P4_OUTDIR)/dash_pipeline.json:/etc/dash/dash_pipeline.json \
		-v $(PWD)/$(P4_OUTDIR)/dash_pipeline_p4rt.txt:/etc/dash/dash_pipeline_p4rt.txt \
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

saithrift-server:
	$(DOCKER_RUN_SAITHRIFT_BLDR) \
	    make $@

DOCKER_RUN_SAITHRIFT_SRVR =\
	docker run \
	--rm \
	$(DOCKER_FLAGS) \
	--net=host \
	--name dash-saithrift-server-$(USER) \
	-v $(PWD)/$(P4_OUTDIR)/dash_pipeline.json:/etc/dash/dash_pipeline.json \
	-v $(PWD)/$(P4_OUTDIR)/dash_pipeline_p4rt.txt:/etc/dash/dash_pipeline_p4rt.txt \
	-v $(PWD)/SAI:/SAI \
	-v $(PWD)/SAI/SAI/meta:/meta \
	-w /SAI/rpc/usr/sbin \
	-e LD_LIBRARY_PATH=/SAI/lib:/usr/local/lib \
	$(DOCKER_SAITHRIFT_BLDR_IMG)

run-saithrift-server:
	$(DOCKER_RUN_SAITHRIFT_SRVR) \
	./saiserver

kill-saithrift-server:
	-docker kill dash-saithrift-server-$(USER)

run-saithrift-server-bash:
	$(DOCKER_RUN_SAITHRIFT_SRVR) \
	/bin/bash

saithrift-server-clean:
	$(DOCKER_RUN_SAITHRIFT_BLDR) \
	    make $@
	rm -rf SAI/rpc

###############################
# SAI TEST TARGETS
###############################

.PHONY:test libsai-test
test:libsai-test

test-clean:
	make -C tests/libsai clean


.PHONY:libsai-test
libsai-test:SAI/SAI SAI/lib/libsai.so
	chmod -R a+w tests/libsai
	$(DOCKER_RUN) \
	    --name dash-build-test-$(USER) \
		-w /tests/libsai  $(DOCKER_BMV2_BLDR_IMG) \
	    make

timeout?=5

.PHONY:run-libsai-test
run-libsai-test:
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
	docker exec -w /tests/libsai/vnet_out simple_switch-$(USER) ./vnet_out

# Make sure we have executable
tests/init_switch/init_switch:libsai-test

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
	docker exec -w /tests/libsai/init_switch simple_switch-$(USER) ./init_switch

###############################
# DOCKER BUILD/PUBLISH TARGETS
###############################

docker-bmv2-bldr:
	docker build \
		-f dockerfiles/Dockerfile.bmv2-bldr \
	    -t $(DOCKER_BMV2_BLDR_IMG) \
	    --build-arg user=$(DASH_USER) \
	    --build-arg group=$(DASH_GROUP) \
	    --build-arg uid=$(DASH_UID) \
	    --build-arg guid=$(DASH_GUID) \
	    --build-arg hostname=$(DASH_HOST) \
	    --build-arg available_processors=$(shell nproc) \
	    dockerfiles

docker-publish-bmv2-bldr:
	echo "TO DO when we have a proper repository"

docker-pull-bmv2-bldr:
	docker pull $(DOCKER_BMV2_BLDR_IMG)
###############################
docker-saithrift-bldr:
	docker build \
		-f dockerfiles/Dockerfile.saithrift-bldr \
	    -t $(DOCKER_SAITHRIFT_BLDR_IMG) \
	    --build-arg user=$(DASH_USER) \
	    --build-arg group=$(DASH_GROUP) \
	    --build-arg uid=$(DASH_UID) \
	    --build-arg guid=$(DASH_GUID) \
	    --build-arg hostname=$(DASH_HOST) \
	    --build-arg available_processors=$(shell nproc) \
		dockerfiles

docker-publish-saithrift-bldr:
	echo "TO DO when we have a proper repository"

docker-pull-saithrift-bldr:
	docker pull $(DOCKER_SAITHRIFT_BLDR_IMG)

###############################
# Builder, has base packages to make client docker
docker-saithrift-client-bldr:
	docker build \
		-f dockerfiles/Dockerfile.saithrift-client-bldr \
	    -t $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG) \
	    --build-arg user=$(DASH_USER) \
	    --build-arg group=$(DASH_GROUP) \
	    --build-arg uid=$(DASH_UID) \
	    --build-arg guid=$(DASH_GUID) \
	    --build-arg hostname=$(DASH_HOST) \
	    --build-arg available_processors=$(shell nproc) \
		./tests

docker-pull-saithrift-client-bldr:
	docker pull $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG)

docker-publish-saithrift-client-bldr:
	echo "TO DO when we have a proper repository"

###############################
		
# Client image, rebuild any time SAI interface changes
# TODO - add sai header (inc/ and experimental) dependencies
docker-saithrift-client:
	docker build \
		-f dockerfiles/Dockerfile.saithrift-client \
	    -t $(DOCKER_SAITHRIFT_CLIENT_IMG) \
		.

DOCKER_RUN_SAITHRIFT_CLIENT=\
	docker run \
	-u root \
	--network=host \
	--rm \
	-w /tests/ \
	$(DOCKER_FLAGS) \

# Run "production" Pytests bundled inside docker
run-saithrift-pytests:deploy-ixiac disable-ipv6
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-w /tests/saithrift/pytest \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	./run-saithrift-pytests.sh

# Run "dev" tests mounted from host
run-saithrift-dev-pytests:deploy-ixiac disable-ipv6
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-v $(PWD)/tests/:/tests-dev/ \
	-w /tests-dev/saithrift/pytest \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	./run-saithrift-pytests.sh

# Run "production" PTF tests bundled inside docker
# Note - if add ixia-c usage to PTF tests, add dependency deploy-ixiac
run-saithrift-ptftests: disable-ipv6
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-w /tests/saithrift/ptf \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	./run-saithrift-ptftests.sh

# Run "dev" PTF tests mounted from host
# Note - if add ixia-c usage to PTF tests, add dependency deploy-ixiac
run-saithrift-dev-ptftests: disable-ipv6
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-v $(PWD)/tests/:/tests-dev/ \
	-w /tests-dev/saithrift/ptf \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	./run-saithrift-ptftests.sh

run-saithrift-client-bash:
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-v $(PWD)/tests/:/tests-dev/ \
	-w /tests-dev/saithrift \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	/bin/bash

###############################

# docker-dash-p4c:
# 	docker build \
# 		-f dockerfiles/Dockerfile.p4c-bmv2 \
# 	    -t $(DOCKER_P4C_BMV2_IMG) \
# 	    --build-arg user=$(USER) \
# 	    --build-arg uid=$(shell id -u) \
# 	    --build-arg guid=$(shell id -g) \
# 	    --build-arg hostname=$(shell echo $$HOSTNAME) \
# 	    --build-arg available_processors=$(shell nproc) \
# 		dockerfiles

docker-dash-p4c:
	docker build \
		-f dockerfiles/Dockerfile.p4c-bmv2 \
	    -t $(DOCKER_P4C_BMV2_IMG) \
	    --build-arg user=$(DASH_USER) \
	    --build-arg group=$(DASH_GROUP) \
	    --build-arg uid=$(DASH_UID) \
	    --build-arg guid=$(DASH_GUID) \
	    --build-arg hostname=$(DASH_HOST) \
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
	    --build-arg user=$(DASH_USER) \
	    --build-arg group=$(DASH_GROUP) \
	    --build-arg uid=$(DASH_UID) \
	    --build-arg guid=$(DASH_GUID) \
	    --build-arg hostname=$(DASH_HOST) \
	    --build-arg available_processors=$(shell nproc) \
		dockerfiles

docker-pull-dash-grpc:
	docker pull $(DOCKER_GRPC_IMG)

docker-publish-dash-grpc:
	echo "TO DO when we have a proper repository"

###############################
# BMV2-PKTGEN NETWORKING TARGETS
###############################

network:veth0 veth2 disable-ipv6

veth0: /sys/class/net/veth0
/sys/class/net/veth0:

	sudo ip link add name veth0 type veth peer name veth1
	sudo ip link set dev veth0 up
	sudo ip link set dev veth1 up
	sudo ip link set veth0 mtu 9500
	sudo ip link set veth1 mtu 9500

veth2: /sys/class/net/veth2
/sys/class/net/veth2:
	sudo ip link add name veth2 type veth peer name veth3
	sudo ip link set dev veth2 up
	sudo ip link set dev veth3 up
	sudo ip link set veth2 mtu 9500
	sudo ip link set veth3 mtu 9500

disable-ipv6:
	./disable_veth_ipv6.sh

# Delete veth's, test existence to avoid needless use of sudo
network-clean:
	@-([ -e /sys/class/net/veth0 ] && sudo ip link delete dev veth0 && echo "Deleted veth0/1") || echo "No veth0, not deleting"
	@-([ -e /sys/class/net/veth2 ] && sudo ip link delete dev veth2 && echo "Deleted veth2/3") || echo "No veth2, not deleting"

###############################
# IXIA-C TARGETS
###############################

run-ixiac-test: ixiac-prereq init-switch
	# python3 -m pytest ../test/test-cases/bmv2_model/ -s

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
