FROM ubuntu:20.04
ARG DEBIAN_FRONTEND = noninteractive
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install -y postgresql postgresql-contrib libpqxx-dev
RUN pip3 install -r requirements.txt
RUN mkdir -p /code
WORKDIR /code
ADD . /code/
RUN chmod +x ./run.sh
