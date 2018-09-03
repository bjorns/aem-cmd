FROM centos:7

RUN yum -y install epel-release
RUN yum -y update
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm
RUN yum -y install python36u
RUN yum -y install python36u-pip

RUN mkdir -p /usr/local/aem-cmd
WORKDIR /usr/local/aem-cmd

COPY acmd ./acmd
COPY bin ./bin
COPY setup.py .
COPY acceptance-test/runtime_requirements.txt ./requirements.txt

RUN pip3.6 install -r requirements.txt
RUN python3.6 setup.py install

COPY acceptance-test/expected ./expected
COPY acceptance-test/verify-installation.sh .

ENTRYPOINT "./verify-installation.sh"
