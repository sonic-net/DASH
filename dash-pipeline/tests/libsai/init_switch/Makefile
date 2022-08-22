all:init_switch
init_switch: init_switch.cpp /SAI/lib/libsai.so
	echo "building $@ ..."
	g++ \
	    -I /SAI/lib \
	    -I /SAI/SAI/inc \
	    -I /SAI/SAI/experimental/ \
	    -o init_switch \
	    init_switch.cpp \
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
	rm -rf init_switch
