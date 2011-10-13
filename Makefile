#!/usr/bin/make

PACKAGE=schooltool.devtools

DIST=/home/ftp/pub/schooltool/trunk
PYTHON=python
BUILDOUT_FLAGS=

.PHONY: all
all: build

.PHONY: build
build: .installed.cfg

python:
	rm -rf python
	virtualenv --no-site-packages -p $(PYTHON) python

.PHONY: bootstrap
bootstrap bin/buildout: python
	python/bin/python bootstrap.py

.PHONY: buildout
buildout .installed.cfg: python bin/buildout buildout.cfg setup.py
	bin/buildout $(BUILDOUT_FLAGS)

.PHONY: bzrupdate
bzrupdate:
	bzr update -q

.PHONY: update
update: bzrupdate
	$(MAKE) buildout BUILDOUT_FLAGS=-n

.PHONY: tags
tags: build
	bin/tags

.PHONY: clean
clean:
	rm -rf python
	rm -rf bin develop-eggs parts .installed.cfg
	rm -rf build
	rm -f ID TAGS tags
	rm -rf coverage
	find . -name '*.py[co]' -delete

.PHONY: realclean
realclean:
	rm -rf eggs
	rm -rf dist
	$(MAKE) clean

# Tests

.PHONY: test
test: build
	bin/test -u

.PHONY: ftest
ftest: build
	bin/test -f

.PHONY: testall
testall: build
	bin/test --at-level 2

# Coverage

.PHONY: coverage
coverage: build
	test -d parts/test/coverage && ! test -d coverage && mv parts/test/coverage . || true
	rm -rf coverage
	bin/test --at-level 2 -u --coverage=coverage
	mv parts/test/coverage .

.PHONY: coverage-reports-html
coverage-reports-html coverage/reports: coverage
	test -d parts/test/coverage && ! test -d coverage && mv parts/test/coverage . || true
	rm -rf coverage/reports
	mkdir coverage/reports
	bin/coverage coverage coverage/reports
	ln -s $(PACKAGE).html coverage/reports/index.html

.PHONY: publish-coverage-reports
publish-coverage-reports: coverage/reports
	@test -n "$(DESTDIR)" || { echo "Please specify DESTDIR"; exit 1; }
	cp -r coverage/reports $(DESTDIR).new
	chmod -R a+rX $(DESTDIR).new
	rm -rf $(DESTDIR).old
	mv $(DESTDIR) $(DESTDIR).old || true
	mv $(DESTDIR).new $(DESTDIR)

.PHONY: ftest-coverage
ftest-coverage: build
	test -d parts/test/ftest-coverage && ! test -d ftest-coverage && mv parts/test/ftest-coverage . || true
	rm -rf ftest-coverage
	bin/test --at-level 2 -f --coverage=ftest-coverage
	mv parts/test/ftest-coverage .

.PHONY: ftest-coverage-reports-html
ftest-coverage-reports-html ftest-coverage/reports: ftest-coverage
	test -d parts/test/ftest-coverage && ! test -d ftest-coverage && mv parts/test/ftest-coverage . || true
	rm -rf ftest-coverage/reports
	mkdir ftest-coverage/reports
	bin/coverage ftest-coverage ftest-coverage/reports
	ln -s $(PACKAGE).html ftest-coverage/reports/index.html

.PHONY: publish-ftest-coverage-reports
publish-ftest-coverage-reports: ftest-coverage/reports
	@test -n "$(DESTDIR)" || { echo "Please specify DESTDIR"; exit 1; }
	cp -r ftest-coverage/reports $(DESTDIR).new
	chmod -R a+rX $(DESTDIR).new
	rm -rf $(DESTDIR).old
	mv $(DESTDIR) $(DESTDIR).old || true
	mv $(DESTDIR).new $(DESTDIR)

# Release

.PHONY: release
release:
	grep -qv 'dev' version.txt.in || echo -n `cat version.txt.in`-r`bzr revno` > version.txt
	$(PYTHON) setup.py sdist
	rm -f version.txt

.PHONY: move-release
move-release:
	mv -v dist/$(PACKAGE)-*dev-r*.tar.gz $(DIST)/dev

# Helpers

.PHONY: ubuntu-environment
ubuntu-environment:
	sudo apt-get install bzr build-essential gettext enscript ttf-liberation \
	    python-all-dev python-virtualenv \
	    libicu-dev libxslt1-dev libfreetype6-dev libjpeg62-dev

