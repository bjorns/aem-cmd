FROM centos:7

RUN yum -y install epel-release
RUN yum -y update

RUN yum -y install python-pip

RUN pip install --upgrade aem-cmd

RUN mkdir -p /usr/local/aem-cmd
WORKDIR /usr/local/aem-cmd

COPY acceptance-test/verify-installation.sh .
COPY acceptance-test/expected ./expected

ENTRYPOINT "./verify-installation.sh"
