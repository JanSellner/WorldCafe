FROM ubuntu:18.04

MAINTAINER Milania

# Install basic tooling
RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
	python3 python3-pip \
 && ln -s $(which python3) /usr/bin/python \
 && ln -s $(which pip3) /usr/bin/pip

# Install latest version of g++ (based on https://askubuntu.com/a/581497)
RUN add-apt-repository ppa:ubuntu-toolchain-r/test \
 && apt-get update \
 && apt-get install -y gcc-9 g++-9 \
 && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 60 --slave /usr/bin/g++ g++ /usr/bin/g++-9

# Copy the app
COPY . /group_app
WORKDIR /group_app

# Build c++ programs and install dependencies
RUN mkdir --parents group_allocation_c++/x64/Release \
 && g++ --std=c++17 -O3 -pthread -o group_allocation_c++/x64/Release/group_allocation_c++.exe group_allocation_c++/group_allocation_c++.cpp \
 && g++ --std=c++17 -O3 -pthread -o group_allocation_c++/x64/Release/performance_tests.exe group_allocation_c++/performance_tests/performance_tests.cpp \
 && pip install -r requirements.txt

CMD ["python", "run_server.py"]
