FROM centos:7

RUN yum -y install epel-release
RUN yum -y update
RUN yum -y install sudo

RUN mkdir -p /usr/local/aem-cmd
WORKDIR /usr/local/aem-cmd

RUN curl https://raw.githubusercontent.com/bjorns/aem-cmd/master/get-acmd.sh | bash

COPY acceptance-test/expected ./expected
COPY acceptance-test/verify-installation.sh .

ENTRYPOINT "./verify-installation.sh"
