FROM ubuntu:16.04

RUN apt update && \
    apt install -y g++ gcc git make automake sudo && \
    apt install -y cmake automake libjudy-dev libgmp-dev libpcap-dev \
    libboost-dev libboost-test-dev libboost-program-options-dev libboost-system-dev \
    libboost-filesystem-dev libboost-thread-dev libevent-dev libtool flex bison pkg-config g++ libssl-dev && \
    apt-get install -y cmake g++ git automake libtool libgc-dev bison flex \
	    libfl-dev libgmp-dev libboost-dev libboost-iostreams-dev \
	    libboost-graph-dev llvm pkg-config python python-scapy python-ipaddr python-ply python3-pip \
	    tcpdump && \
    pip3 install  scapy ply && \
    apt-get install -y autoconf automake libtool curl make g++ unzip

RUN git clone https://github.com/protocolbuffers/protobuf.git && \
    cd protobuf && \
	git checkout v3.6.1 && \
	git submodule update --init --recursive && \
	./autogen.sh && \
	./configure && \
	make && \
        make install && ldconfig && \
        cd .. && rm -rf protobuf

RUN git clone --recursive https://github.com/p4lang/p4c.git && \
    cd p4c && \
	git submodule update --init --recursive && \
	mkdir build && \
	cd build && \
	cmake .. && \
	make && \
	make install && \
        cd / && \
        rm -rf p4lang

RUN pip3 install six

RUN apt-get update && apt-get install -y lsb-release

RUN pip3 install ipaddr

RUN git clone https://github.com/marian-pritsak/behavioral-model && \
        cd behavioral-model && \
	bash install_deps.sh && \
        ./autogen.sh && \
        ./configure && \
        make && \
        make install && \
        cd .. && \
        rm -rf behavioral-model

ENV LD_LIBRARY_PATH /usr/local/lib/

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
