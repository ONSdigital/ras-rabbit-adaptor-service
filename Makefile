.PHONY: build test

build:
	pip3 install -U pipenv
	pipenv install --dev

test:
	pipenv run flake8 --exclude ./lib/*
	pipenv run python -m unittest discover
