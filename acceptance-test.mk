centos7-py2-local:
	docker build -f acceptance-test/Dockerfile.$@ -t acmd-$@ .
	docker run acmd-$@

centos7-py2-pip:
	docker build -f acceptance-test/Dockerfile.$@ -t acmd-$@ .
	docker run acmd-$@

centos7-py2-shell:
	docker build -f acceptance-test/Dockerfile.$@ -t acmd-$@ .
	docker run acmd-$@

centos7-py3-local:
	docker build -f acceptance-test/Dockerfile.$@ -t acmd-$@ .
	docker run acmd-$@

ubuntu17-py2-pip:
	docker build -f acceptance-test/Dockerfile.$@ -t acmd-$@ .
	docker run acmd-$@

acceptance-test: centos7-py2-local centos7-py2-pip centos7-py2-shell centos7-py3-local ubuntu17-py2-pip