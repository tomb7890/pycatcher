test:	lint clean
	@python3 -m pytest --capture=no -x -q test/


web:
	@python3 app.py --report
	cp report.html ~/public_html/report.html 

lint:	tags
	@python3 -m flake8

tags:
	@etags `find . -type f -iname  \\*py`

clean:
	@-rm __pycache__/*pyc report.html
	@-rm test/__pycache__/*pyc
