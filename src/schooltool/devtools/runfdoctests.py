#!/usr/bin/env python
"""Hacky script for a fast feedback loop with SchoolTool's functional tests.

The problem with functional doctests is that the initial setup (ZCML parsing
etc.) takes ages, and then your brand new and shiny functional doctest fails
because of a silly typo.  You fix the typo and wait 30 seconds to find another
one.  The feedback loop is just too slow for efficient development.

Hence this script.  Run it in the root of your SchoolTool source tree, and
enter a pathname of a functional doctest file at the prompt.  When you get
that proverbial silly typo on line 17, just fix it and use readline's history
to rerun the same test file.  You'll get feedback in seconds.
"""

import os
import sys
import readline
from StringIO import StringIO

from doctest import (DocTestCase, REPORTING_FLAGS,
                     _unittest_reportflags,
                     DocTestRunner,
                     DocTestParser)
import zope.testrunner

def interactiveRunTest(self):
    test = self._dt_test
    old = sys.stdout
    new = StringIO()
    optionflags = self._dt_optionflags

    if not (optionflags & REPORTING_FLAGS):
        # The option flags don't include any reporting flags,
        # so add the default reporting flags
        optionflags |= _unittest_reportflags

    runner = DocTestRunner(optionflags=optionflags,
                           checker=self._dt_checker, verbose=False)
    def write(value):
        if isinstance(value, unicode):
            value = value.encode('utf8')
        new.write(value)

    try:
        runner.DIVIDER = "-"*70
        failures, tries = runner.run(
            test, out=write, clear_globs=False)
    finally:
        sys.stdout = old

    if (failures and test.filename.endswith('.txt')):
        print new.getvalue()
        print "This test failed, wanna try again?"
        while True:
            command = raw_input("fdoctest> ")
            if command.lower() in ["q", "quit", "exit", "n", "no", "c"]:
                break
            elif command.lower() in ["y", "yes"]:
                try:
                    # XXX more hack hack hack
                    self.tearDown()
                    self.setUp()
                    new = StringIO()
                    parser = DocTestParser()
                    test = parser.get_doctest(open(test.filename).read(),
                                              test.globs, test.name,
                                              test.filename, test.lineno,
                                              optionflags)
                    failures, tries = runner.run(
                        test, out=write, clear_globs=False)
                except Exception, e:
                    sys.stdout = old
                    import traceback
                    traceback.print_exc()
                sys.stdout = old
                if not failures:
                    print "The test has passed."
                else:
                    print new.getvalue()
                    print "This test has failed, wanna try again?"
            elif command.lower() in ["l", "p"]:
                print new.getvalue()
    if failures:
        raise self.failureException(self.format_failure(new.getvalue()))

def main():
    args = sys.argv[1:]
    # Hack hack hack!
    DocTestCase.runTest = interactiveRunTest
    # Tab completion
    readline.set_completer_delims(' \t\n')
    readline.parse_and_bind('tab: complete')
    include_eggs = ['schooltool']
    params = []
    import pkg_resources
    for egg_spec in include_eggs:
        try:
            egg = pkg_resources.require(egg_spec)
            params.extend(['--test-path', os.path.abspath(egg[0].location)])
        except pkg_resources.DistributionNotFound:
            pass

    zope.testrunner.run(params + ['--tests-pattern', '^f?tests$'])

if __name__ == '__main__':
    main()
