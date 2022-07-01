FROM p4lang/behavioral-model:no-pi
LABEL maintainer="SONIC-DASH Community"
LABEL description="DASH pipeline P4 Behavioral Model and toolchain"

# Configure make to run as many parallel jobs as cores available
ARG available_processors
ARG MAKEFLAGS=-j$available_processors


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
    make install && \
    cd / && \
    rm -rf grpc

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


RUN pip install jinja2

ENV DEBIAN_FRONTEND noninteractive

ENV BM_RUNTIME_DEPS libboost-program-options1.71.0 \
                    libboost-system1.71.0 \
                    libboost-filesystem1.71.0 \
                    libboost-thread1.71.0 \
                    libgmp10 \
                    libpcap0.8 \
                    python3 \
                    python-is-python3 \
                    sudo

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
