#!/usr/bin/make
#
# Makefile for schooltool.devtools Buildout
#

BOOTSTRAP_PYTHON=python2.5

.PHONY: all
all: build

.PHONY: build
build:
	test -d python || $(MAKE) BOOTSTRAP_PYTHON=$(BOOTSTRAP_PYTHON) bootstrap
	test -f bin/test || $(MAKE) buildout

.PHONY: bootstrap
bootstrap:
	$(BOOTSTRAP_PYTHON) bootstrap.py

.PHONY: buildout
buildout:
	bin/buildout

.PHONY: update
update: build
	bin/buildout -n

.PHONY: test
test: build
	bin/test -u

.PHONY: testall
testall: build
	bin/test

.PHONY: ftest
ftest: build
	bin/test -f

.PHONY: release
release:
	echo -n `sed -e 's/\n//' version.txt.in` > version.txt
	echo -n "_r" >> version.txt
	bzr revno >> version.txt
	bin/buildout setup setup.py sdist

.PHONY: move-release
move-release:
	 mv dist/schooltool.devtools-*.tar.gz /home/ftp/pub/schooltool/releases/nightly

.PHONY: coverage
coverage: build
	rm -rf coverage
	bin/test -u --coverage=coverage
	mv parts/test/coverage .
	@cd coverage && ls | grep -v tests | xargs grep -c '^>>>>>>' | grep -v ':0$$' | cat

.PHONY: coverage-reports-html
coverage-reports-html:
	rm -rf coverage/reports
	mkdir coverage/reports
	bin/coverage
	ln -s schooltool.devtools.html coverage/reports/index.html

.PHONY: ubuntu-environment
ubuntu-environment:
	@if [ `whoami` != "root" ]; then { \
	 echo "You must be root to create an environment."; \
	 echo "I am running as $(shell whoami)"; \
	 exit 3; \
	} else { \
	 apt-get install subversion build-essential python-all python-all-dev libc6-dev libicu-dev; \
	 apt-get build-dep python-imaging; \
	 apt-get build-dep python-libxml2 libxml2; \
	 echo "Installation Complete: Next... Run 'make'."; \
	} fi
