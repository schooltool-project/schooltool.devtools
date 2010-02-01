#!/usr/bin/make

PACKAGE=schooltool.devtools

DIST=/home/ftp/pub/schooltool/1.4
BOOTSTRAP_PYTHON=python2.5
BUILDOUT_FLAGS=

.PHONY: all
all: build

.PHONY: build
build: bin/test

.PHONY: bootstrap
bootstrap bin/buildout:
	$(BOOTSTRAP_PYTHON) bootstrap.py

.PHONY: buildout
buildout bin/test: bin/buildout setup.py buildout.cfg
	bin/buildout $(BUILDOUT_FLAGS)
	@touch --no-create bin/test

.PHONY: bzrupdate
bzrupdate:
	bzr update -q

.PHONY: update
update: bzrupdate
	$(MAKE) buildout BUILDOUT_FLAGS=-n

.PHONY: test
test: build
	bin/test -u

.PHONY: release
release: bin/buildout
	echo -n `cat version.txt.in`_r`bzr revno` > version.txt
	bin/buildout setup setup.py sdist
	rm version.txt

.PHONY: move-release
move-release:
	mv -v dist/$(PACKAGE)-*.tar.gz $(DIST)/dev

.PHONY: coverage
coverage: build
	test -d parts/test/coverage && ! test -d coverage && mv parts/test/coverage . || true
	rm -rf coverage
	bin/test --at-level 2 -u --coverage=coverage
	mv parts/test/coverage .

.PHONY: coverage-reports-html
coverage-reports-html coverage/reports:
	test -d parts/test/coverage && ! test -d coverage && mv parts/test/coverage . || true
	rm -rf coverage/reports
	mkdir coverage/reports
	bin/coverage coverage coverage/reports
	ln -s $(PACKAGE).html coverage/reports/index.html

.PHONY: clean
clean:
	rm -rf bin develop-eggs parts python
	rm -rf build dist
	rm -f .installed.cfg
	rm -f ID TAGS tags
	find . -name '*.py[co]' -delete

.PHONY: ubuntu-environment
ubuntu-environment:
	@if [ `whoami` != "root" ]; then { \
	 echo "You must be root to create an environment."; \
	 echo "I am running as $(shell whoami)"; \
	 exit 3; \
	} else { \
	 apt-get install bzr build-essential python-all-dev libc6-dev libicu-dev libxslt1-dev; \
	 apt-get install libfreetype6-dev libjpeg62-dev; \
	 echo "Installation Complete: Next... Run 'make'."; \
	} fi
