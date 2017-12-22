all: ubuntu-pip centos7-pip

ubuntu-pip:
	docker build -f Dockerfile.$@ -t acmd_$@ .
	docker run acmd_$@

centos7-pip:
	docker build -f Dockerfile.$@ -t acmd_$@ .
	docker run acmd_$@

.PHONY: all ubuntu-pip centos7-pip
