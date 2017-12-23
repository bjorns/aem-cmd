centos7-py2-local:
	docker build -f acceptance-test/Dockerfile.$@ -t acmd-$@ .
	docker run acmd-$@

centos7-py2-pip:
	docker build -f Dockerfile.$@ -t acmd_$@ .
	docker run acmd_$@

ubuntu17-py2-pip:
	docker build -f Dockerfile.$@ -t acmd_$@ .
	docker run acmd_$@

