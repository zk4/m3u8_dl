
rm:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -type d -iname '*egg-info' -exec rm -rdf {} +
	rm -f .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf proxy.py.egg-info
	rm -rf .pytest_cache
	rm -rf .hypothesis
	rm -rdf assets
	

test: rm
	pytest -s -v  tests/

coverage-html:
	# --cov where you want to cover
	#  tests  where your test code is 
	pytest --cov=m3_dl/ --cov-report=html tests/
	open htmlcov/index.html

coverage:
	pytest --cov=m3_dl/ tests/

main:
	python3 -m m3_dl eat -c 2

install: uninstall
	pip3 install . 

uninstall:
	pip3 uninstall -y m3_dl

run:
	python3 -m m3_dl "./index-v1-a1.m3" "./a/a.mp4" -d -t 4 -p socks5h://127.0.0.1:5993
	# python3 -m m3_dl "https://liaoning.olevod.eu/VMDIR510864250940453C919A769590642977/20190807/EGS10Y4Z/1000kb/hls/index.m3?date=1581518050&token=586e0cc6c0101176a966542cb0a5aae0" "./b/a.mp4"
	

all: rm uninstall install run 


pure-all: env-rm rm env install test run


	
upload-to-test: rm
	python3 setup.py bdist_wheel --universal
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*


upload-to-prod: rm
	python3 setup.py bdist_wheel --universal
	twine upload dist/*


freeze:
	# pipreqs will find the module the project really depneds
	pipreqs . --force

freeze-global:
	#  pip3 will find all the module not belong to standard  library
	pip3 freeze > requirements.txt


env-rm:
	rm -rdf env


env:
	python3 -m venv env
	. env/bin/activate

