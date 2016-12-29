all:
	pip install --user -r requirements.txt 
	python setup.py build
	python setup.py install --user
	$(HOME)/.lback/bin/lback --adduser --username "ROOT" --password "ROOT"

