FROM ubuntu:17.10

RUN apt-get update
RUN apt-get install -y python-pip

RUN pip install --upgrade aem-cmd

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

ENTRYPOINT ["./verify-installation.sh", "-c"]
