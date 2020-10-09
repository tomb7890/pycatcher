test:	lint clean
	python3 -m pytest --capture=no test/


lint:	tags
	python3 -m flake8

tags:
	etags `find . -type f -iname  \\*py`

clean:
	-rm __pycache__/*pyc
	-rm test/__pycache__/*pyc
