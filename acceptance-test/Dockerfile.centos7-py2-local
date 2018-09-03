FROM centos:7

RUN yum -y install epel-release
RUN yum -y update
RUN yum -y install python-pip
RUN pip install --upgrade pip

RUN mkdir -p /usr/local/aem-cmd
WORKDIR /usr/local/aem-cmd

COPY acmd ./acmd
COPY bin ./bin
COPY setup.py .
COPY acceptance-test/runtime_requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
RUN pip install .

COPY acceptance-test/expected ./expected
COPY acceptance-test/verify-installation.sh .

ENTRYPOINT "./verify-installation.sh"
