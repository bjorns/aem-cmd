all: dist

clean:
	rm -rf dist build aem_cmd.egg-info test_reports .coverage
	rm -f *.log
	find . | grep \.pyc$ | xargs rm -rf

dist: clean
	python setup.py bdist_wheel --universal

test_release: dist
	twine upload -r pypitest dist/*

release: dist
	twine upload -r pypi dist/*

test2:
	nosetests-2.7 --with-coverage --cover-package=acmd --cover-min-percentage=80 --cover-html --cover-html-dir=build/test_reports

test3:
	nosetests-3.4

test: test3 test2

include ./acceptance-test.mk


.PHONY: all clean dist test_release release lint test2 test3 test acceptance-test
