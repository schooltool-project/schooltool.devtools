#!/usr/bin/make

PACKAGE=schooltool.devtools

DIST=/home/ftp/pub/schooltool/flourish
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
bootstrap bin/buildout: | buildout.cfg python
	python/bin/python bootstrap.py

buildout.cfg:
	cp deploy.cfg buildout.cfg

.PHONY: buildout
buildout .installed.cfg: python bin/buildout buildout.cfg base.cfg deploy.cfg setup.py
	bin/buildout $(BUILDOUT_FLAGS)

.PHONY: develop
develop bin/coverage: buildout.cfg develop.cfg
	sed -e 's/base.cfg/develop.cfg/' -i buildout.cfg
	$(MAKE) buildout

.PHONY: update
update:
	bzr up
	$(MAKE) buildout BUILDOUT_FLAGS=-n

.PHONY: tags
tags: build
	bin/ctags

.PHONY: clean
clean:
	rm -rf python
	rm -rf bin develop-eggs parts .installed.cfg
	rm -rf build
	rm -f ID TAGS tags
	rm -rf coverage ftest-coverage
	find . -name '*.py[co]' -delete

.PHONY: realclean
realclean:
	rm -f buildout.cfg
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
	rm -rf coverage
	bin/test --at-level 2 -u --coverage=$(CURDIR)/coverage

.PHONY: coverage-reports-html
coverage-reports-html coverage/reports: bin/coverage build
	test -d coverage || $(MAKE) coverage
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
	rm -rf ftest-coverage
	bin/test --at-level 2 -f --coverage=$(CURDIR)/ftest-coverage

.PHONY: ftest-coverage-reports-html
ftest-coverage-reports-html ftest-coverage/reports: bin/coverage build
	test -d ftest-coverage || $(MAKE) ftest-coverage
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
	-cp buildout.cfg buildout.cfg~dev~
	cp deploy.cfg buildout.cfg
	grep -qv 'dev' version.txt.in || echo -n `cat version.txt.in`-r`bzr revno` > version.txt
	$(PYTHON) setup.py sdist
	rm -f version.txt
	-mv buildout.cfg~dev~ buildout.cfg

.PHONY: move-release
move-release: upload
	rm -v dist/$(PACKAGE)-*dev-r*.tar.gz

.PHONY: upload
upload:
	set -e ;\
	VERSION=`cat version.txt.in` ;\
	DIST=$(DIST) ;\
	grep -qv 'dev' version.txt.in || VERSION=`cat version.txt.in`-r`bzr revno` ;\
	grep -qv 'dev' version.txt.in || DIST=$(DIST)/dev ;\
	if [ -w $${DIST} ] ; then \
	    echo cp dist/$(PACKAGE)-$${VERSION}.tar.gz $${DIST} ;\
	    cp dist/$(PACKAGE)-$${VERSION}.tar.gz $${DIST} ;\
	else \
	    echo scp dist/$(PACKAGE)-$${VERSION}.tar.gz* schooltool.org:$${DIST} ;\
	    scp dist/$(PACKAGE)-$${VERSION}.tar.gz* schooltool.org:$${DIST} ;\
	fi

# Helpers

.PHONY: ubuntu-environment
ubuntu-environment:
	sudo apt-get install build-essential gettext enscript \
	    python-dev python-virtualenv \
	    ttf-ubuntu-font-family ttf-liberation \
	    libicu-dev libxslt1-dev libfreetype6-dev libjpeg-dev

