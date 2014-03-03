FROM stackbrew/ubuntu
MAINTAINER crashandcompile@markgius.com

RUN apt-get install python

ADD ./run_test.sh /run_test.sh
RUN chmod +x ./run_test.sh
CMD ./run_test.sh
