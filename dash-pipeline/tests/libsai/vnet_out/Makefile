all:vnet_out
vnet_out: vnet_out.cpp /SAI/lib/libsai.so
	echo "building $@ ..."
	g++ \
	    -I /SAI/SAI/inc \
	    -I /SAI/SAI/experimental/ \
	    -o vnet_out \
	    vnet_out.cpp \
	    -Wl,-rpath,/SAI/lib \
	    -L/SAI/lib/ \
	    -lsai \
	    -L/usr/local/lib/ \
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
		-laddress_sorting \
	    -g

clean:
	rm -rf vnet_out
