vnet_out: vnet_out.cpp
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
	echo "built $@"
	pwd
	ls -l
clean:
	rm -rf vnet_out
