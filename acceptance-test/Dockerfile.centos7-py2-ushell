FROM centos:7

RUN yum -y install epel-release
RUN yum -y update
RUN yum -y install sudo
RUN yum -y install which

RUN mkdir -p /usr/local/aem-cmd
WORKDIR /usr/local/aem-cmd


RUN useradd -g users local_user

USER local_user

COPY acceptance-test/expected ./expected
COPY acceptance-test/verify-installation.sh .

# Requires path to .local/bin dir where acmd is installed
ENV PATH="/home/local_user/.local/bin:${PATH}"
RUN curl https://raw.githubusercontent.com/bjorns/aem-cmd/master/get-acmd-user.sh | bash

ENTRYPOINT "./verify-installation.sh"
