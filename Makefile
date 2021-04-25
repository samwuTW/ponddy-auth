SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
CIRCLE_TAG ?= $(shell git describe --tags --abbrev=0)

pip:  ## Install all pip packages
	pip3 install pip-tools
	pip-compile requirements/develop.in
	pip-compile requirements/base.in
	pip-sync requirements/develop.txt requirements/base.txt

build:  ## Build App
	pip3 uninstall -y ponddy_auth || echo "No uninstall requirement"
	CIRCLE_TAG=$(CIRCLE_TAG) python3 setup.py bdist_wheel
.PHONY: build

install: build  ## Install the app locally
	pip3 install dist/*.whl
.PHONY: install

ci: typecheck lint test ## Run all checks (test, lint, typecheck)
.PHONY: ci

test: install ## Run tests
	python3 -m pytest tests
	coverage report -m && coverage html --show-contexts
	pip3 uninstall -y ponddy_auth
.PHONY: test

lint:  ## Run linting
	python3 -m black --check src
	python3 -m isort -c src
	python3 -m flake8 src
	python3 -m pydocstyle src
.PHONY: lint

lint-fix:  ## Run autoformatters
	python3 -m black src
	python3 -m isort src
.PHONY: lint-fix

typecheck:  ## Run typechecking
	python3 -m mypy --show-error-codes --pretty src/ponddy_auth
.PHONY: typecheck

tox:  ## Run tox
	tox
.PHONY: tox

clean:  ## Clean all things
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' | xargs rm -rf
	@rm -rf build/
	@rm -rf dist/
	@rm -rf src/*.egg*
	@rm -f .coverage.*
	@rm -rf htmlcov
.PHONY: clean

push:  ## Push code with tags
	git push && git push --tags
.PHONY: push

.DEFAULT_GOAL := help
help: Makefile
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'
