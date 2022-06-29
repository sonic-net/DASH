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
	    -g

		#	    -labsl \
		# -lz \

clean:
	rm -rf vnet_out
