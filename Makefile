all: dist

clean:
	rm -rf dist build aem_cmd.egg-info test_reports

dist:
	python setup.py bdist_wheel

test:
	nosetests --with-coverage --cover-package=acmd --cover-min-percentage=75 --cover-html --cover-html-dir=build/test_reports

.PHONY: all clean dist test