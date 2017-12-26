centos7-%:
	docker build -f acceptance-test/Dockerfile.$@ -t acmd-$@ . > /tmp/docker_build
	docker run acmd-$@

ubuntu17-%:
	docker build -f acceptance-test/Dockerfile.$@ -t acmd-$@ . > /tmp/docker_build
	docker run acmd-$@

# Acceptance tests local code to verify release
acceptance-test: centos7-py2-local centos7-py3-local ubuntu17-py2-local ubuntu17-py3-local
	@echo "Acceptance Test Successful"

# Verification test runs released code to verify release
verification-test: centos7-py2-pip centos7-py2-shell centos7-py2-ushell ubuntu17-py2-pip
	@echo "Verification Test Successful"


