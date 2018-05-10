.PHONY:	local test testcov deploy start stop

local:
	heroku local web

test:
	python -m unittest discover -s tests -p "*_tests.py"

testcov:
	coverage run -m unittest discover -s tests -p "*_tests.py" && coverage report -m && coverage html

deploy:
	git push heroku master

start:
	heroku ps:scale web=1

stop:
	heroku ps:scale web=0
