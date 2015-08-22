clean:
	rm -rf dist build aem_cmd.egg-info

dist:
	python setup.py bdist_wheel

test:
	nosetests --with-coverage --cover-package=acmd --cover-min-percentage=60 --cover-html --cover-html-dir=build/test_reports
