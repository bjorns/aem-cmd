FROM ubuntu:17.10

RUN apt-get update
RUN apt-get install -y python-pip

RUN pip install --upgrade aem-cmd

RUN mkdir -p /usr/local/aem-cmd
WORKDIR /usr/local/aem-cmd

COPY acceptance-test/verify-installation.sh .
COPY acceptance-test/expected ./expected

ENTRYPOINT ["./verify-installation.sh", "-c"]
