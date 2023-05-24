SHELL = /bin/bash

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

# "All" type targets for convenience
all:p4 sai saithrift-server docker-saithrift-client docker-saichallenger-client test

run-all-tests:run-libsai-test run-saithrift-client-tests run-saichallenger-tests
run-saithrift-client-tests: run-saithrift-ptftests run-saithrift-pytests
run-saithrift-client-dev-tests: run-saithrift-dev-ptftests run-saithrift-dev-pytests

.PHONY:clean
clean: kill-all p4-clean sai-clean test-clean network-clean saithrift-server-clean
	rm -rf $(P4_OUTDIR)

kill-all: kill-saithrift-server kill-switch undeploy-ixiac kill-saichallenger-client

PWD := $(realpath $(mkfile_dir))
DASH_USER ?=dashuser
DASH_GROUP ?=dashusers
DASH_UID ?=4321
DASH_GUID?=4321
DASH_HOST?=dash

ENABLE_DOCKER_PULL ?= y

# Include file defines DOCKER_GRPC_IMG_NAME and DOCKER_GRPC_IMG_CTAG
include dockerfiles/DOCKER_GRPC_IMG.env

# Slimmed-down version bmv2 backend only
# include file defines DOCKER_P4C_BMV2_IMG
include dockerfiles/DOCKER_P4C_BMV2_IMG.env

# Slimmed-down version dpdk backend only
# include file defines DOCKER_P4C_DPDK_IMG
include dockerfiles/DOCKER_P4C_DPDK_IMG.env

# Builds sai-P4rt clients to run inside bmv2 process
# include file defines DOCKER_BMV2_BLDR_IMG_NAME and DOCKER_BMV2_BLDR_IMG_CTAG
include dockerfiles/DOCKER_BMV2_BLDR_IMG.env

# Runs bmv2 process - consider slimmer if don't need sai/p4rt clients inside
DOCKER_BMV2_RUN_IMG ?=$(DOCKER_BMV2_BLDR_IMG)

# Compiles sai headers, libsai, saithrift server & client/server libs
# include file defines DOCKER_SAITHRIFT_BLDR_IMG_NAME and DOCKER_SAITHRIFT_BLDR_IMG_CTAG
include dockerfiles/DOCKER_SAITHRIFT_BLDR_IMG.env

# Base image with test frameworks, DASH client libs not installed
# include file defines DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_NAME and DOCKER_SAITHRIFT_CLIENT_BLDR_CTAG
include dockerfiles/DOCKER_SAITHRIFT_CLIENT_BLDR_IMG.env

# Client image built locally with saithrift client libs + PTF & Pytest frameworks
DOCKER_SAITHRIFT_CLIENT_IMG ?= local/dash-saithrift-client:latest

# Base image with test frameworks, not installed
# include file defines DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG_name and DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG_CTAG
include dockerfiles/DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG.env

# SAIChallenger Client image built locally with saithrift client libs + PTF & Pytest frameworks
DOCKER_SAI_CHALLENGER_CLIENT_IMG ?= local/dash-saichallenger-client:latest

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

SHA1SUM := sha1sum | awk '{print substr($$1,0,11);}'

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
	@echo "Compile P4 program $(P4_MAIN) for bmv2 ..."
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
		-DTARGET_BMV2_V1MODEL \
	    $(P4_MAIN) \
		-b bmv2 \
		-o $(P4_OUTDIR) \
	    --p4runtime-files $(P4_OUTDIR)/dash_pipeline_p4rt.json,$(P4_OUTDIR)/dash_pipeline_p4rt.txt

# DPDK - experimental/WIP

P4_DPDK_OUTDIR=dpdk-pna/dash_pipeline.dpdk

p4c-dpdk-pna:
	@echo "Compile P4 program $(P4_MAIN) for dpdk-pna ..."
	mkdir -p $(P4_DPDK_OUTDIR) && \
	chmod o+w $(P4_DPDK_OUTDIR) && \
	docker run \
	--rm \
	--name dash-p4c-dpdk-$(USER) \
	-u $(DASH_USER) \
	$(DOCKER_FLAGS) \
	-v $(PWD)/bmv2:/bmv2 \
	-v $(PWD)/dpdk-pna:/dpdk-pna \
	-w / \
	$(DOCKER_P4C_DPDK_IMG)  \
	p4c-dpdk -DTARGET_DPDK_PNA -DPNA_CONNTRACK --pp $(P4_DPDK_OUTDIR)/dash_pipeline.pp.p4 \
		-o $(P4_DPDK_OUTDIR)/dash_pipeline.spec --arch pna \
		--bf-rt-schema $(P4_DPDK_OUTDIR)/dash_pipeline.p4.bfrt.json \
		--p4runtime-files $(P4_DPDK_OUTDIR)/dash_pipeline.p4.p4info.txt \
		$(P4_MAIN)


	# p4c-dpdk -DDPDK_PNA -DPNA_CONNTRACK --dump $(P4_DPDK_OUTDIR) --pp $(P4_DPDK_OUTDIR)/dash_pipeline.pp.p4 \
	# -o $(P4_DPDK_OUTDIR)/dash_pipeline.spec --arch pna --bf-rt-schema $(P4_DPDK_OUTDIR)/dash_pipeline.p4.bfrt.json \
	# --p4runtime-files $(P4_DPDK_OUTDIR)/dash_pipeline.p4.p4info.txt $(P4_MAIN)

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

sai-headers: p4 docker-saithrift-bldr-image-exists | SAI/SAI
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

saithrift-server: docker-saithrift-bldr-image-exists
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

saithrift-server-clean: docker-saithrift-bldr-image-exists
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

DOCKER_BMV2_BLDR_IMG_TAG = $(shell cat dockerfiles/Dockerfile.bmv2-bldr | $(SHA1SUM))
DOCKER_BMV2_BLDR_IMG = $(DOCKER_BMV2_BLDR_IMG_NAME):$(DOCKER_BMV2_BLDR_IMG_TAG)

docker-bmv2-bldr:
	{ [ x$(ENABLE_DOCKER_PULL) == xy ] && docker pull $(DOCKER_BMV2_BLDR_IMG); } || \
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
	[ -n $(DOCKER_BMV2_BLDR_IMG_CTAG) ] && \
		docker tag $(DOCKER_BMV2_BLDR_IMG) \
		$(DOCKER_BMV2_BLDR_IMG_NAME):$(DOCKER_BMV2_BLDR_IMG_CTAG)

docker-pull-bmv2-bldr:
	docker pull $(DOCKER_BMV2_BLDR_IMG)

# Only used for CI publishing to save artifact between jobs:
docker-save-bmv2-bldr:
	docker save --output bmv2-bldr-image.tar $(DOCKER_BMV2_BLDR_IMG)
docker-load-bmv2-bldr:
	docker load --input bmv2-bldr-image.tar

docker-publish-bmv2-bldr:
	@echo "Publish $(DOCKER_BMV2_BLDR_IMG) - requires credentials, can only do from DASH repo, not a fork"
	docker push $(DOCKER_BMV2_BLDR_IMG)
	[ -n $(DOCKER_BMV2_BLDR_IMG_CTAG) ] && \
		docker push $(DOCKER_BMV2_BLDR_IMG_NAME):$(DOCKER_BMV2_BLDR_IMG_CTAG)

###############################
# Ubuntu docker image SHA
# amd64/ubuntu:20.04 on 2022-07-03
AMD64_UBUNTU_20_04 := b2339eee806d44d6a8adc0a790f824fb71f03366dd754d400316ae5a7e3ece3e
# amd64/ubuntu:22.04 on 2023-05-16
AMD64_UBUNTU_22_04 := ca5534a51dd04bbcebe9b23ba05f389466cf0c190f1f8f182d7eea92a9671d00

AMD64_UBUNTU_SHA256 ?= $(AMD64_UBUNTU_22_04)

DOCKER_SAITHRIFT_BLDR_IMG_TAG = $(shell cat dockerfiles/Dockerfile.saithrift-bldr | sed 's/ubuntu_image_sha/$(AMD64_UBUNTU_SHA256)/g' | $(SHA1SUM))
DOCKER_SAITHRIFT_BLDR_IMG = $(DOCKER_SAITHRIFT_BLDR_IMG_NAME):$(DOCKER_SAITHRIFT_BLDR_IMG_TAG)

docker-saithrift-bldr-image-exists:
	docker images --format "{{.Repository}}:{{.Tag}}" | grep $(DOCKER_SAITHRIFT_BLDR_IMG) || make docker-saithrift-bldr

docker-saithrift-bldr:
	{ [ x$(ENABLE_DOCKER_PULL) == xy ] && docker pull $(DOCKER_SAITHRIFT_BLDR_IMG); } || \
	docker build \
		-f dockerfiles/Dockerfile.saithrift-bldr \
	    -t $(DOCKER_SAITHRIFT_BLDR_IMG) \
	    --build-arg ubuntu_image_sha=$(AMD64_UBUNTU_SHA256) \
	    --build-arg user=$(DASH_USER) \
	    --build-arg group=$(DASH_GROUP) \
	    --build-arg uid=$(DASH_UID) \
	    --build-arg guid=$(DASH_GUID) \
	    --build-arg hostname=$(DASH_HOST) \
	    --build-arg available_processors=$(shell nproc) \
		dockerfiles
	[ -n $(DOCKER_SAITHRIFT_BLDR_IMG_CTAG) ] && \
		docker tag $(DOCKER_SAITHRIFT_BLDR_IMG) \
		$(DOCKER_SAITHRIFT_BLDR_IMG_NAME):$(DOCKER_SAITHRIFT_BLDR_IMG_CTAG)

docker-pull-saithrift-bldr:
	docker pull $(DOCKER_SAITHRIFT_BLDR_IMG)

docker-publish-saithrift-bldr:
	@echo "Publish $(DOCKER_SAITHRIFT_BLDR_IMG) - requires credentials, can only do from DASH repo, not a fork"
	docker push $(DOCKER_SAITHRIFT_BLDR_IMG)
	[ -n $(DOCKER_SAITHRIFT_BLDR_IMG_CTAG) ] && \
		docker push $(DOCKER_SAITHRIFT_BLDR_IMG_NAME):$(DOCKER_SAITHRIFT_BLDR_IMG_CTAG)

###############################
# Builder, has base packages to make client docker

DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_TAG = $(shell cat dockerfiles/Dockerfile.saithrift-client-bldr | $(SHA1SUM))
DOCKER_SAITHRIFT_CLIENT_BLDR_IMG = $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_NAME):$(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_TAG)

docker-saithrift-client-bldr:
	{ [ x$(ENABLE_DOCKER_PULL) == xy ] && docker pull $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG); } || \
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
	[ -n $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_CTAG) ] && \
		docker tag $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG) \
		$(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_NAME):$(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_CTAG)

docker-pull-saithrift-client-bldr:
	docker pull $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG)

docker-publish-saithrift-client-bldr:
	@echo "Publish $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG) - requires credentials, can only do from DASH repo, not a fork"
	docker push $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG)
	[ -n $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_CTAG) ] && \
		docker push $(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_NAME):$(DOCKER_SAITHRIFT_CLIENT_BLDR_IMG_CTAG)

###############################

# Client image, rebuild any time SAI interface changes
# TODO - add sai header (inc/ and experimental) dependencies
docker-saithrift-client:
	docker build \
		-f dockerfiles/Dockerfile.saithrift-client \
	    -t $(DOCKER_SAITHRIFT_CLIENT_IMG) \
		..

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
	-w /ci-tests/saithrift/pytest \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	./run-saithrift-pytests.sh

# Run "dev" tests mounted from host
run-saithrift-dev-pytests:deploy-ixiac disable-ipv6
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-v $(PWD)/tests/:/ci-tests-dev/ \
	-w /ci-tests-dev/saithrift/pytest \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	./run-saithrift-pytests.sh

# Run "production" PTF tests bundled inside docker
# Note - if add ixia-c usage to PTF tests, add dependency deploy-ixiac
run-saithrift-ptftests: disable-ipv6
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-w /tests/ \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	./functional/ptf/run-tests.sh

# Run "dev" PTF tests mounted from host
# Note - if add ixia-c usage to PTF tests, add dependency deploy-ixiac
run-saithrift-dev-ptftests: disable-ipv6
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-v $(PWD)/../test/test-cases/:/tests-dev/ \
	-w /tests-dev/ \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	./functional/ptf/run-tests.sh

run-saithrift-client-bash:
	$(DOCKER_RUN_SAITHRIFT_CLIENT) \
	-v $(PWD)/../test/test-cases/:/tests-dev/ \
	-w /tests-dev/ \
	$(DOCKER_SAITHRIFT_CLIENT_IMG) \
	/bin/bash

###############################


DOCKER_P4C_BMV2_IMG_TAG = $(shell cat dockerfiles/Dockerfile.p4c-bmv2 | $(SHA1SUM))
DOCKER_P4C_BMV2_IMG = $(DOCKER_P4C_BMV2_IMG_NAME):$(DOCKER_P4C_BMV2_IMG_TAG)

docker-dash-p4c:
	{ [ x$(ENABLE_DOCKER_PULL) == xy ] && docker pull $(DOCKER_P4C_BMV2_IMG); } || \
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
	[ -n $(DOCKER_P4C_BMV2_IMG_CTAG) ] && \
		docker tag $(DOCKER_P4C_BMV2_IMG) $(DOCKER_P4C_BMV2_IMG_NAME):$(DOCKER_P4C_BMV2_IMG_CTAG)

docker-pull-dash-p4c:
	docker pull $(DOCKER_P4C_BMV2_IMG)

docker-publish-dash-p4c:
	@echo "Publish $(DOCKER_P4C_BMV2_IMG) - requires credentials, can only do from DASH repo, not a fork"
	docker push $(DOCKER_P4C_BMV2_IMG)
	[ -n $(DOCKER_P4C_BMV2_IMG_CTAG) ] && \
		docker push $(DOCKER_P4C_BMV2_IMG_NAME):$(DOCKER_P4C_BMV2_IMG_CTAG)

###############################

DOCKER_P4C_DPDK_IMG_TAG = $(shell cat dockerfiles/Dockerfile.p4c-dpdk | $(SHA1SUM))
DOCKER_P4C_DPDK_IMG = $(DOCKER_P4C_DPDK_IMG_NAME):$(DOCKER_P4C_DPDK_IMG_TAG)

docker-dash-p4c-dpdk:
	{ [ x$(ENABLE_DOCKER_PULL) == xy ] && docker pull $(DOCKER_P4C_DPDK_IMG); } || \
	docker build \
		-f dockerfiles/Dockerfile.p4c-dpdk \
	    -t $(DOCKER_P4C_DPDK_IMG) \
	    --build-arg user=$(DASH_USER) \
	    --build-arg group=$(DASH_GROUP) \
	    --build-arg uid=$(DASH_UID) \
	    --build-arg guid=$(DASH_GUID) \
	    --build-arg hostname=$(DASH_HOST) \
	    --build-arg available_processors=$(shell nproc) \
		dockerfiles
	[ -n $(DOCKER_P4C_DPDK_IMG_CTAG) ] && \
		docker tag $(DOCKER_P4C_DPDK_IMG) $(DOCKER_P4C_DPDK_IMG_NAME):$(DOCKER_P4C_DPDK_IMG_CTAG)

docker-pull-dash-p4c-dpdk:
	docker pull $(DOCKER_P4C_DPDK_IMG)

docker-publish-dash-p4c-dpdk:
	@echo "Publish $(DOCKER_P4C_DPDK_IMG) - requires credentials, can only do from DASH repo, not a fork"
	docker push $(DOCKER_P4C_DPDK_IMG)
	[ -n $(DOCKER_P4C_DPDK_IMG_CTAG) ] && \
		docker push $(DOCKER_P4C_DPDK_IMG_NAME):$(DOCKER_P4C_DPDK_IMG_CTAG)

###############################

DOCKER_GRPC_IMG_TAG = $(shell cat dockerfiles/Dockerfile.grpc1.43.2 | $(SHA1SUM))
DOCKER_GRPC_IMG = $(DOCKER_GRPC_IMG_NAME):$(DOCKER_GRPC_IMG_TAG)

docker-dash-grpc:
	{ [ x$(ENABLE_DOCKER_PULL) == xy ] && docker pull $(DOCKER_GRPC_IMG); } || \
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
	[ -n $(DOCKER_GRPC_IMG_CTAG) ] && docker tag $(DOCKER_GRPC_IMG) $(DOCKER_GRPC_IMG_NAME):$(DOCKER_GRPC_IMG_CTAG)

docker-pull-dash-grpc:
	docker pull $(DOCKER_GRPC_IMG)

docker-publish-dash-grpc:
	@echo "Publish $(DOCKER_GRPC_IMG) - requires credentials, can only do from DASH repo, not a fork"
	docker push $(DOCKER_GRPC_IMG)
	[ -n $(DOCKER_GRPC_IMG_CTAG) ] && docker push $(DOCKER_GRPC_IMG_NAME):$(DOCKER_GRPC_IMG_CTAG)

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
# SAI-CHALLENGER TARGETS
###############################

SAI_CHALLENGER_PATH = $(PWD)/../test/SAI-Challenger

CONTAINER_SAI_CHALLENGER_CLIENT_NAME = dash-saichallenger-client-$(USER)

# Add passing parameters to the run-saichallenger-tests target.
ifeq (run-saichallenger-tests,$(firstword $(MAKECMDGOALS)))
  SAI_CHALLENGER_SETUP_FILE := $(wordlist 2, 2, $(MAKECMDGOALS))
  SAI_CHALLENGER_TEST := $(wordlist 3, 3, $(MAKECMDGOALS))
  $(eval $(SAI_CHALLENGER_SETUP_FILE):;@:)
  $(eval $(SAI_CHALLENGER_TEST):;@:)
endif
# If setup file's isn't passed, set it to the default.
ifeq ($(SAI_CHALLENGER_SETUP_FILE),)
SAI_CHALLENGER_SETUP_FILE := sai_dpu_client_server_snappi.json
endif
# If test's name isn't passed, set it to the default.
ifeq ($(SAI_CHALLENGER_TEST),)
SAI_CHALLENGER_TEST := .
endif

DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG_TAG = $(shell cat dockerfiles/Dockerfile.saichallenger-client-bldr | $(SHA1SUM))
DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG = $(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG_NAME):$(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG_TAG)

docker-saichallenger-client-bldr:
	{ [ x$(ENABLE_DOCKER_PULL) == xy ] && docker pull $(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG); } || \
		{ pushd $(SAI_CHALLENGER_PATH) && git submodule update --init && ./build.sh -i client && popd; \
		docker build \
			-f dockerfiles/Dockerfile.saichallenger-client-bldr \
			-t $(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG) \
			. ;\
		}
	[ -n $(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG_CTAG) ] && \
		docker tag $(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG) \
		$(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG_NAME):$(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG_CTAG)

docker-publish-saichallenger-client-bldr:
	@echo "Publish $(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG) - requires credentials, can only do from DASH repo, not a fork"
	docker push $(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG)

docker-pull-saichallenger-client-bldr:
	docker pull $(DOCKER_SAI_CHALLENGER_CLIENT_BLDR_IMG)

docker-saichallenger-client: docker-saichallenger-client-bldr
	docker build \
		-f dockerfiles/Dockerfile.saichallenger-client \
		-t $(DOCKER_SAI_CHALLENGER_CLIENT_IMG) \
		.

DOCKER_RUN_SAI_CHALLENGER_CLIENT=docker run \
	-v $(SAI_CHALLENGER_PATH):/sai-challenger \
	-v $(SAI_CHALLENGER_PATH)/../test-cases/scale/saic/:/sai-challenger/dash_tests/scale \
	-v $(SAI_CHALLENGER_PATH)/../test-cases/functional/saic/:/sai-challenger/dash_tests/functional \
	-v $(SAI_CHALLENGER_PATH)/../test-cases/utils/:/sai-challenger/dash_tests/utils \
	-v $(PWD)/../:/dash \
	--cap-add=NET_ADMIN \
	--device /dev/net/tun:/dev/net/tun \
	--rm \
	--network=host \
	--name $(CONTAINER_SAI_CHALLENGER_CLIENT_NAME)

run-saichallenger-client: deploy-ixiac
	$(DOCKER_RUN_SAI_CHALLENGER_CLIENT) \
	-d \
	--name $(CONTAINER_SAI_CHALLENGER_CLIENT_NAME) \
	$(DOCKER_SAI_CHALLENGER_CLIENT_IMG)

run-saichallenger-client-bash: deploy-ixiac
	$(DOCKER_RUN_SAI_CHALLENGER_CLIENT) \
	-w /sai-challenger/dash_tests \
	$(DOCKER_FLAGS) \
	$(DOCKER_SAI_CHALLENGER_CLIENT_IMG) \
	/bin/bash

kill-saichallenger-client:
	-docker kill $(CONTAINER_SAI_CHALLENGER_CLIENT_NAME)

run-saichallenger-tests: run-saichallenger-functional-tests run-saichallenger-scale-tests

run-saichallenger-functional-tests: deploy-ixiac
	$(DOCKER_RUN_SAI_CHALLENGER_CLIENT) \
	-w /sai-challenger/dash_tests/functional \
	$(DOCKER_FLAGS) \
	$(DOCKER_SAI_CHALLENGER_CLIENT_IMG) \
	./run-tests.sh --setup=$(SAI_CHALLENGER_SETUP_FILE) $(SAI_CHALLENGER_TEST)

run-saichallenger-scale-tests: deploy-ixiac
	$(DOCKER_RUN_SAI_CHALLENGER_CLIENT) \
	-w /sai-challenger/dash_tests/scale \
	$(DOCKER_FLAGS) \
	$(DOCKER_SAI_CHALLENGER_CLIENT_IMG) \
	./run-tests.sh --setup=$(SAI_CHALLENGER_SETUP_FILE) $(SAI_CHALLENGER_TEST)

run-saichallenger-tutorials: deploy-ixiac
	$(DOCKER_RUN_SAI_CHALLENGER_CLIENT) \
	-w /sai-challenger/dash_tests/functional \
	$(DOCKER_FLAGS) \
	$(DOCKER_SAI_CHALLENGER_CLIENT_IMG) \
	./run-tests.sh --setup=$(SAI_CHALLENGER_SETUP_FILE) tutorial

###############################
# ENVIRONMENT SETUP TARGETS
###############################

install-docker-compose:
	sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$$(uname -s)-$$(uname -m)" -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
