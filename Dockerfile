FROM ubuntu:24.04

# Set the correct locale so that non-ASCII characters can be processed correctly (https://stackoverflow.com/questions/28405902/how-to-set-the-locale-inside-a-ubuntu-docker-container/38553499#38553499)
# And set correct timezone (https://stackoverflow.com/questions/40234847/docker-timezone-in-ubuntu-16-04-image)
RUN apt update && apt install -y \
           locales \
           tzdata \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG=en_US.UTF-8 \
    && ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

ENV LANG=en_US.UTF-8

# Install basic tooling
RUN apt update && apt install -y \
    software-properties-common \
    build-essential \
	python3 python3-venv python3-pip python-is-python3

# Don't mess around with the system python (via https://pythonspeed.com/articles/activate-virtualenv-dockerfile/)
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the app
COPY group_allocation_c++ /group_app/group_allocation_c++
COPY requirements.txt /group_app/requirements.txt
WORKDIR /group_app

# Build c++ programs and install dependencies
RUN mkdir --parents group_allocation_c++/x64/Release \
 && g++ -O3 -pthread -o group_allocation_c++/x64/Release/group_allocation_c++.exe group_allocation_c++/group_allocation_c++.cpp \
 && g++ -O3 -pthread -o group_allocation_c++/x64/Release/performance_tests.exe group_allocation_c++/performance_tests/performance_tests.cpp \
 && pip install -r requirements.txt

COPY . /group_app

CMD ["python", "run_server.py"]
