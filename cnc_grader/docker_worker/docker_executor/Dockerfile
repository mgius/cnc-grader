FROM stackbrew/ubuntu
MAINTAINER crashandcompile@markgius.com

RUN apt-get update
RUN apt-get install -y python ruby openjdk-7-jdk gcc g++ perl

ADD ./test_executor.py /test_executor.py
RUN chmod +x ./test_executor.py
