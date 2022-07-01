vnet_out: vnet_out.cpp
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

		#	    -labsl \
		# -lz \

clean:
	rm -rf vnet_out
