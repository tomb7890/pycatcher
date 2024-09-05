test:	lint clean
	@python3 -m pytest --capture=no -x -q test/


web:
	@python3 app.py --report
	cp report.html ~/public_html/report.html 

lint:	tags
	~/.local/bin/black *py
	@python3 -m flake8

tags:
	@ctags -e   `find . -type f -iname  \\*py`

clean:
	@-rm __pycache__/*pyc 
	@-rm test/__pycache__/*pyc
	rm -f report.html > /dev/null
