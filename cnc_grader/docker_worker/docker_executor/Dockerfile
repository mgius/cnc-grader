FROM ubuntu:15.10
MAINTAINER crashandcompile@markgius.com

RUN apt-get update && apt-get install --no-install-recommends -y python ruby openjdk-8-jdk gcc g++ perl

ADD ./test_executor.py /test_executor.py
RUN chmod +x ./test_executor.py
