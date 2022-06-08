FROM p4lang/behavioral-model:no-pi
LABEL maintainer="P4 Developers <p4-dev@lists.p4.org>"
LABEL description="This Docker image includes all of the PI artifacts, \
including the Thrift-based PI implementation for the bmv2 backend. It is \
currently used to run CI tests."

# Default to using 2 make jobs, which is a good default for CI. If you're
# building locally or you know there are more cores available, you may want to
# override this.
ARG MAKEFLAGS=-j

# Select the type of image we're building. Use `build` for a normal build, which
# is optimized for image size. Use `test` if this image will be used for
# testing; in this case, the source code and build-only dependencies will not be
# removed from the image.
ARG IMAGE_TYPE=test

# Select the compiler to use.
# We install the default version of GCC (GCC 9), as well as clang 8 and clang 10.
ARG sswitch_grpc=yes
ARG CC=gcc
ARG CXX=g++
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV GIT_SSL_NO_VERIFY=true

ENV PI_DEPS automake \
            build-essential \
            clang-8 \
            clang-10 \
            clang-format-8 \
            g++ \
            libboost-dev \
            libboost-system-dev \
            libboost-thread-dev \
            libtool \
            libtool-bin \
            pkg-config \
            libreadline-dev \
            libpcap-dev \
            libmicrohttpd-dev \
            doxygen \
            valgrind \
                vim \
                git-core \
                python3 \
                cmake \
                python3-pip
ENV PI_RUNTIME_DEPS libboost-system1.71.0 \
                    libboost-thread1.71.0 \
                    libpcap0.8 \
                    python3 \
                    python-is-python3

RUN apt-get update && apt-get install -y --no-install-recommends $PI_DEPS $PI_RUNTIME_DEPS

RUN cd / && git clone --depth=1 -b v1.43.2 https://github.com/google/grpc.git && \
    cd grpc/ && \
    git submodule update --init --recursive && \
    mkdir -p cmake/build && \
    cd cmake/build && \
    cmake -DBUILD_SHARED_LIBS=ON -DgRPC_INSTALL=ON --parallel 1 ../.. && \
    make  && \
    make install

ENV LD_LIBRARY_PATH=/usr/local/lib

WORKDIR /
# COPY proto/sysrepo/docker_entry_point.sh /docker_entry_point.sh
# COPY . /PI/
RUN git clone https://github.com/p4lang/PI
WORKDIR /PI/
RUN git submodule update --init --recursive
RUN apt-get update && \
    ./autogen.sh && \
    ./configure --enable-Werror --with-bmv2 --with-proto --with-cli --with-internal-rpc --with-sysrepo && \
    ./proto/sysrepo/install_yangs.sh && \
    make && \
    make install


# RUN git clone https://github.com/marian-pritsak/DASH-1.git && \
RUN pip install gitpython
RUN pip install jinja2
# ./sai_api_gen.py rt_sirius.json --ignore-tables=appliance,eni_meter,slb_decap         --sai-git-url=https://github.com/marian-pritsak/SAI.git         --sai-git-branch=base         --impl_filepath=./impl.cpp         dash 
#g++ -I./SAI/inc/ -I./SAI/experimental/ impl.cpp -L/usr/local/lib/ -lpiprotogrpc -lpiprotobuf -lprotobuf -lgrpc++ -lpiall -lpi_dummy

ENV DEBIAN_FRONTEND noninteractive

RUN apt update && \
    apt install -y g++ gcc git make automake sudo && \
    apt install -y cmake automake libjudy-dev libgmp-dev libpcap-dev \
    libboost-dev libboost-test-dev libboost-program-options-dev libboost-system-dev \
    libboost-filesystem-dev libboost-thread-dev libevent-dev libtool flex bison pkg-config g++ libssl-dev && \
    apt-get install -y cmake g++ git automake libtool libgc-dev bison flex \
	    libfl-dev libgmp-dev libboost-dev libboost-iostreams-dev \
	    libboost-graph-dev llvm pkg-config python python-ply python3-pip \
	    tcpdump && \
    pip3 install  scapy ply ipaddr && \
    apt-get install -y autoconf automake libtool curl make g++ unzip


 RUN git clone --recursive https://github.com/p4lang/p4c.git && \
     cd p4c && \
 	git submodule update --init --recursive && \
 	mkdir build && \
 	cd build && \
 	cmake --parallel 1 .. && \
 	make && \
 	make install

ENV BM_RUNTIME_DEPS libboost-program-options1.71.0 \
                    libboost-system1.71.0 \
                    libboost-filesystem1.71.0 \
                    libboost-thread1.71.0 \
                    libgmp10 \
                    libpcap0.8 \
                    python3 \
                    python-is-python3

RUN apt-get update && apt-get install -y git

WORKDIR /

RUN git clone https://github.com/p4lang/behavioral-model.git

WORKDIR /behavioral-model/

RUN apt-get update -qq && \
    apt-get install -qq --no-install-recommends $BM_DEPS $BM_RUNTIME_DEPS && \
    ./autogen.sh && \
    ./configure --with-pdfixed --with-pi --with-stress-tests --enable-debugger --enable-coverage --enable-Werror && \
    make  && \
    make install

WORKDIR /

ARG user
ARG uid
ARG guid
ARG hostname

ENV BUILD_HOSTNAME $hostname
ENV USER $user

RUN groupadd -f -r -g $guid g$user

RUN useradd $user -l -u $uid -g $guid -d /var/$user -m -s /bin/bash

RUN echo "$user ALL=(ALL) NOPASSWD:ALL" >>/etc/sudoers

USER $user
