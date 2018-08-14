all: format lint test

format:
	black src 

format.check:
	black src --check

lint:
	flake8 src

test:
	py.test

check: format.check lint
