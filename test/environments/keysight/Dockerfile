FROM ubuntu:focal

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=US/Pacific

RUN apt -y update
RUN apt -y upgrade

RUN apt -y install build-essential
RUN apt -y install git
RUN apt -y install wget

RUN apt -y install python3
RUN apt -y install python3-setuptools
RUN apt -y install python3-pip

COPY . /keysight
WORKDIR /keysight

RUN pip install -r ./requirements.txt

LABEL author="Mircea Dan Gheorghe"
LABEL version="1.0"
LABEL description="DASH env for Keysight"
