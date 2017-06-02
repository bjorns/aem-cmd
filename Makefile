all: dist

clean:
	rm -rf dist build aem_cmd.egg-info test_reports .coverage
	rm -f *.log
	find . | grep \.pyc$ | xargs rm

dist: clean
	python setup.py bdist_wheel

test_release: dist
	twine upload -r pypitest dist/*

release: dist
	twine upload -r pypi dist/*

lint:
	pylint --rcfile=pylint.rc acmd

test2:
	nosetests-2.7 --with-coverage --cover-package=acmd --cover-min-percentage=80 --cover-html --cover-html-dir=build/test_reports

test3:
	nosetests-3.4

test: test3 test2

.PHONY: all clean dist lint test
