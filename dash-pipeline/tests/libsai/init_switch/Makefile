
INC=-I /SAI/SAI/inc -I /SAI/SAI/experimental/
SRC=init_switch.cpp
OBJ=$(SRC:.cpp=.o)

all: init_switch

%.o: %.cpp
	g++ $(INC) -c $< -o $@

init_switch: $(OBJ) /SAI/lib/libsai.so
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
	rm -f init_switch *.o
