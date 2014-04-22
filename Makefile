TAGSFILES=$(shell ls *py)

tags:
	@etags $(TAGSFILES)

test:	tags
	@python -m unittest discover -p '*Test*.py' 	

report:	test
	python Application.py --verbose --debug --localrss --report

wbur:	test
	python Application.py --verbose --debug --localrss --program=wbur

all:	test report



