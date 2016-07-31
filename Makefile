all:
	pip install -r requirements.txt 
	python setup.py build
	python setup.py install
	lback --adduser --username "ROOT" --password "ROOT"

