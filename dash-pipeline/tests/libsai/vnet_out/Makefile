
INC=-I /SAI/SAI/inc -I /SAI/SAI/experimental/
SRC=vnet_out.cpp
OBJ=$(SRC:.cpp=.o)

all: vnet_out

%.o: %.cpp
	g++ $(INC) -c $< -o $@

vnet_out: $(OBJ) /SAI/lib/libsai.so
	echo "building $@ ..."
	g++ $(OBJ) \
	    -o $@ \
	    -Wl,-rpath,/SAI/lib \
	    -L/SAI/lib/ \
	    -lsai \
	    -L/usr/local/lib/ \
	    -lprotobuf \
		-lpiprotobuf \
		-lpiprotogrpc \
		-lgrpc++ \
	    -g

clean:
	rm -f vnet_out *.o
