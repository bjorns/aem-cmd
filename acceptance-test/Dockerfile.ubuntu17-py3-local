FROM ubuntu:17.10

RUN apt-get update
RUN apt-get install -y python3-pip

RUN pip3 install --upgrade aem-cmd

RUN mkdir -p /usr/local/aem-cmd
WORKDIR /usr/local/aem-cmd

COPY acmd ./acmd
COPY bin ./bin
COPY setup.py .
COPY acceptance-test/runtime_requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install .

COPY acceptance-test/expected ./expected
COPY acceptance-test/verify-installation.sh .

ENTRYPOINT ["./verify-installation.sh", "-c"]
