all: saithrift-server saithrift-server-install
# SAI submodule used by below targets; modified in-place!
SAI=$(shell pwd)/../SAI
# Host dir where saithrift artifacts will be installed
LIB=$(shell pwd)/../lib
RPC_INST_DIR=$(shell pwd)/../rpc

META=../SAI/meta

SAIRPC_VENDOR_EXTRA_LIBS?=
SAIRPC_EXTRA_LIBS= "$(SAIRPC_VENDOR_EXTRA_LIBS) \
		-L/lib/x86_64-linux-gnu -Wl,-rpath=/lib/x86_64-linux-gnu -lm \
		-L/usr/local/lib/ -Wl,-rpath=/usr/local/lib \
	    -lpthread \
	    -lpiprotogrpc \
	    -lpiprotobuf \
	    -lprotobuf \
	    -lgrpc++ \
	    -lgrpc \
	    -lpiall \
	    -lpi_dummy \
	    -lpthread \
	    -labsl_synchronization \
	    -labsl_status \
		-labsl_raw_hash_set \
		-lgpr \
		-lre2 \
		-lssl \
		-laddress_sorting"

# Below based on: https://github.com/opencomputeproject/SAI/blob/master/ptf/SAI_PTF_user-guide.md
# Dependencies are assumed to be installed, e.g. in the docker container
saithrift-server:
	# Copy headers to /usr/include/sai
	sudo mkdir -p /usr/include/sai
	sudo cp $(SAI)/inc/sai*.h /usr/include/sai/
	# Following is workaround for https://github.com/opencomputeproject/SAI/issues/1537
	sudo cp $(SAI)/experimental/sai*.h /usr/include/sai/
	sudo cp -r $(SAI)/experimental/ /usr/include/

	# Install vendor specific SAI library i.e. DASH bmv2 libsai.so in /usr/lib.
	sudo cp $(LIB)/libsai.so /usr/lib

	@echo "Build SAI thrift server and libraries..."
	mkdir -p $(RPC_INST_DIR) && chmod a+w $(RPC_INST_DIR)

	cd $(SAI) && export SAITHRIFTV2=y && \
		export GEN_SAIRPC_OPTS="-ve" && \
		export SAIRPC_EXTRA_LIBS=$(SAIRPC_EXTRA_LIBS) && \
		make saithrift-build && \
		export DESTDIR=$(RPC_INST_DIR) && make saithrift-install

	# NOTE: commands below is a workaround (WA) and needed until packaging of SAI python is fixed.
	# Re-generate python SAI thrift library again

	cd $(SAI)/test/saithriftv2 && export DESTDIR=$(RPC_INST_DIR) && make install-pylib
	# Copy auto-generated python SAI thrift library to your Test controller host.
	cp $(SAI)/test/saithriftv2/dist/saithrift-0.9.tar.gz $(RPC_INST_DIR)

	# Copy thrift libs from builder image onto host
	cp /usr/lib/libthrift*so* /usr/lib/thrift-0.11.0.tar.gz $(RPC_INST_DIR)
	chmod -R a+w $(META)/generated $(META)/html $(META)/xml $(RPC_INST_DIR)

saithrift-server-clean:
	cd $(SAI) && export SAITHRIFTV2=y  && make clean
	rm -rf $(SAI)/test/saithriftv2/gen-cpp/
	rm -rf $(SAI)/test/saithriftv2/obj/
	rm -rf $(RPC_INST_DIR)
	
clean: saithrift-server-clean
