all: sai-thrift-server
# SAI submodule used by below targets; modified in-place!
SAI=../SAI
# Host dir where sai-thrift artifacts will be installed
LIB=../lib

META=../SAI/meta

# Below based on: https://github.com/opencomputeproject/SAI/blob/088627dd90c3420daf96d294c661b4a152afb01e/ptf/SAI_PTF_user-guide.md
# Dependencies are assumed to be installed, e.g. in the docker container
sai-thrift-server:
	# Copy headers to /usr/include/sai
	sudo mkdir -p /usr/include/sai
	sudo cp $(SAI)/inc/sai*.h $(SAI)/experimental/*.h /usr/include/sai/

	# Install vendor specific SAI library i.e. DASH bmv2 libsai.so in /usr/lib.
	sudo cp $(LIB)/libsai.so /usr/lib

	@echo "Build SAI thrift server and libraries..."

	cd $(SAI) && export SAITHRIFTV2=y && export GEN_SAIRPC_OPTS="-ve" && make saithrift-build saithrift-install

	# NOTE: commands below is a workaround (WA) and needed until packaging of SAI python is fixed.
	# Re-generate python SAI thrift library again

	cd $(SAI)/test/saithriftv2 && make install-pylib
	# Copy auto-generated python SAI thrift library to your Test controller host.
	cp $(SAI)/test/saithriftv2/dist/saithrift-0.9.tar.gz $(LIB)

	# Copy thrift libs from builder image onto host
	cp /thrift-0.11.0/lib/py/dist/* $(LIB)

sai-thrift-server-clean:
	cd $(SAI) && export SAITHRIFTV2=y  && make clean
	rm -rf $(SAI)/test/saithriftv2/gen-cpp/
	rm -rf $(SAI)/test/saithriftv2/obj/
	
clean: sai-thrift-server-clean
