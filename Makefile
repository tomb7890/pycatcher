test:	lint 
	python3 -m pytest test/


lint:	tags
	python3 -m flake8

tags:
	etags `find . -type f -iname  \\*py`

clean:
	rm *pyc
