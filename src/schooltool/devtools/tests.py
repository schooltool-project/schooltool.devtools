#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2009 Shuttleworth Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
Unit tests for schooltool.devtools

$Id$
"""

import doctest
import unittest
import os
from cStringIO import StringIO
import tempfile

from zope.app.locales import pygettext
from zope.i18nmessageid import Message

from schooltool.devtools.selenium_recipe import unflatten_options


def doctest_STPOTEntry():
    r"""This class represents a single message entry in the POT file.

    >>> from schooltool.devtools.i18nextract import STPOTEntry

    >>> class FakeFile(object):
    ...     def write(self, data):
    ...         print data,

    Let's create a message entry:

    >>> entry = STPOTEntry(Message("test", default="default"))
    >>> entry.addComment("# Some comment")
    >>> entry.addLocationComment(os.path.join("path", "file"), 10)

    Then we feed it a fake file:

    >>> output = StringIO()
    >>> entry.write(FakeFile())
    # Some comment
    #: path/file:10
    #. Default: "default"
    msgid "test"
    msgstr ""

    Multiline default values generate correct comments:

    >>> entry = STPOTEntry(Message("test", default="\nline1\n\tline2"))
    >>> entry.write(FakeFile())
    #. Default: ""
    #.  "line1\n"
    #.  "\tline2"
    msgid "test"
    msgstr ""

    We have modified STPOTEntry to be sorted by locations rather than comments.
    If locations match, msgid is compared.

    >>> entry1 = STPOTEntry(Message("A message"))
    >>> entry1.addLocationComment('src/dir1/foo.bar', 10)
    >>> entry1.addLocationComment('src/dir2/baz.bar', 10)

    >>> entry2 = STPOTEntry(Message("A message"))
    >>> entry2.addComment('# B comment')
    >>> entry2.addLocationComment('src/dir1/foo.bar', 12)

    >>> entry3 = STPOTEntry(Message("April"))
    >>> entry3.addComment('# A comment')
    >>> entry3.addLocationComment('src/dir2/baz.bar', 8)

    >>> entry4 = STPOTEntry(Message("May"))
    >>> entry4.addLocationComment('src/dir2/baz.bar', 8)

    >>> for e in sorted([entry1, entry2, entry3, entry4]):
    ...     e.write(FakeFile())
    ...     print '------'
    #: src/dir1/foo.bar:10
    #: src/dir2/baz.bar:10
    msgid "A message"
    msgstr ""
    ------
    # B comment
    #: src/dir1/foo.bar:12
    msgid "A message"
    msgstr ""
    ------
    # A comment
    #: src/dir2/baz.bar:8
    msgid "April"
    msgstr ""
    ------
    #: src/dir2/baz.bar:8
    msgid "May"
    msgstr ""
    ------

    """


def parse_ini_string(ini):
    result = {}
    for line in ini.splitlines():
        args = line.split('=')
        if len(args) < 2:
            continue
        result[args[0].strip()] = '='.join(args[1:]).strip()
    return unflatten_options(result)


def doctest_ScriptFactory():
    r"""Tests for Selenium recipe ScriptFactory

        >>> from schooltool.devtools.webdriver import ScriptFactory
        >>> maker = ScriptFactory()

    Default firefox driver script.

        >>> print maker('firefox', {})
        import selenium.webdriver.firefox.webdriver
        schooltool.devtools.selenium_recipe.factories['firefox'] =\
            lambda config=None: selenium.webdriver.firefox.webdriver.WebDriver()

    Customized default firefox driver.

        >>> print maker('firefox', parse_ini_string('''
        ...     profile = ff/profile
        ...     timeout = 30
        ...     binary = /usr/bin/firefox
        ...     '''))
        import selenium.webdriver.firefox.webdriver
        from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
        from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
        schooltool.devtools.selenium_recipe.factories['firefox'] =\
            lambda config=None: selenium.webdriver.firefox.webdriver.WebDriver(firefox_binary=FirefoxBinary('/usr/bin/firefox'), firefox_profile=FirefoxProfile('/.../ff/profile'), timeout=30)

    Non-default driver named firefox4.

        >>> print maker('firefox4', {})
        Traceback (most recent call last):
        ...
        BadOptions: Need to specify selenium webdriver
                    (selenium.firefox4.web_driver) for 'firefox4'

    Non-default driver with web_driver specified.

        >>> print maker('firefox4', parse_ini_string('''
        ...     web_driver = firefox
        ...     binary = /usr/bin/firefox4
        ...     '''))
        import selenium.webdriver.firefox.webdriver
        from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
        schooltool.devtools.selenium_recipe.factories['firefox4'] =\
            lambda config=None: selenium.webdriver.firefox.webdriver.WebDriver(firefox_binary=FirefoxBinary('/usr/bin/firefox4'))

    IE driver.

        >>> print maker('ie', parse_ini_string('''
        ...     timeout = 50
        ...     port = 80
        ...     '''))
        import selenium.webdriver.ie.webdriver
        schooltool.devtools.selenium_recipe.factories['ie'] =\
            lambda config=None: selenium.webdriver.ie.webdriver.WebDriver(port=80, timeout=50)

    Chrome driver, default.

        >>> print maker('chrome', parse_ini_string('''
        ...     binary = /usr/bin/chromium-driver
        ...     port = 80
        ...     '''))
        import selenium.webdriver.chrome.webdriver
        schooltool.devtools.selenium_recipe.factories['chrome'] =\
            lambda config=None: selenium.webdriver.chrome.webdriver.WebDriver(desired_capabilities={'platform': 'ANY', 'browserName': 'chrome', 'version': '', 'javascriptEnabled': True}, executable_path='/usr/bin/chromium-driver', port=80, config=config)

    Chrome driver, modified to accept capabilities.  Needed for Linux chrome driver.

        >>> print maker('linux_chrome', parse_ini_string('''
        ...     binary = /usr/bin/chromium-driver
        ...     capabilities.chrome.binary = /usr/bin/chromium-browser
        ...     '''))
        import schooltool.devtools.webdriver
        schooltool.devtools.selenium_recipe.factories['linux_chrome'] =\
            lambda config=None: schooltool.devtools.webdriver.ChromeWebDriver(desired_capabilities={'platform': 'ANY', 'browserName': 'chrome', 'version': '', 'chrome.binary': '/usr/bin/chromium-browser', 'javascriptEnabled': True}, executable_path='/usr/bin/chromium-driver', config=config)


    Remote driver.

        >>> print maker('remote', {})
        Traceback (most recent call last):
        ...
        BadOptions: Must set "capabilities" for remote WebDriver 'remote'

    Remote driver with inherited capabilities.

        >>> print maker('builbot_iphone', parse_ini_string('''
        ...     web_driver = remote
        ...     capabilities = iphone
        ...     '''))
        import selenium.webdriver.remote.webdriver
        schooltool.devtools.selenium_recipe.factories['builbot_iphone'] =\
            lambda config=None: selenium.webdriver.remote.webdriver.WebDriver(desired_capabilities={'platform': 'MAC', 'browserName': 'iPhone', 'version': '', 'javascriptEnabled': True})

    Remote driver with bad capabilities.

        >>> print maker('builbot_opera', parse_ini_string('''
        ...     web_driver = remote
        ...     capabilities = whambam
        ...     '''))
        Traceback (most recent call last):
        ...
        BadOptions: "capabilities" for 'builbot_opera' should be custom or one of:
          ANDROID, CHROME, FIREFOX, HTMLUNIT, HTMLUNITWITHJS,
          INTERNETEXPLORER, IPAD, IPHONE, OPERA.

    Remote driver with custom capabilities.

        >>> print maker('buildroid', parse_ini_string('''
        ...     web_driver = remote
        ...     capabilities.browserName = android
        ...     capabilities.version =
        ...     capabilities.platform = LINUX
        ...     capabilities.javascriptEnabled = True
        ...     '''))
        import selenium.webdriver.remote.webdriver
        schooltool.devtools.selenium_recipe.factories['buildroid'] =\
            lambda config=None: selenium.webdriver.remote.webdriver.WebDriver(desired_capabilities={'javascriptEnabled': True, 'browserName': 'android', 'version': '', 'platform': 'LINUX'})

    """


def doctest_STPOTMaker_write():
    r"""Test for POTMaker.write

        >>> from schooltool.devtools.i18nextract import STPOTMaker
        >>> f, path = tempfile.mkstemp()
        >>> pm = STPOTMaker(path, '', 'domain')
        >>> pm.add({'msgid1': [('file2.py', 2), ('file1.py', 3)],
        ...         'msgid2': [('file1.py', 5)]})

        >>> from zope.app.locales.pygettext import make_escapes
        >>> make_escapes(0)
        >>> pm.write()
        >>> f = open(path)
        >>> print f.read()
        # SchoolTool - common information systems platform for school administration
        # Copyright (c) 2007    Shuttleworth Foundation
        #
        # This program is free software; you can redistribute it and/or modify
        # it under the terms of the GNU General Public License as published by
        # the Free Software Foundation; either version 2 of the License, or
        # (at your option) any later version.
        #
        # This program is distributed in the hope that it will be useful,
        # but WITHOUT ANY WARRANTY; without even the implied warranty of
        # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        # GNU General Public License for more details.
        #
        # You should have received a copy of the GNU General Public License
        # along with this program; if not, write to the Free Software
        # Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
        msgid ""
        msgstr ""
        "Project-Id-Version: domain\n"
        "POT-Creation-Date: ...-...-... ...:...0\n"
        "PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
        "Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
        "Language-Team: Schooltool Development Team <schooltool-dev@schooltool.org>\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=UTF-8\n"
        "Content-Transfer-Encoding: 8bit\n"
        "Generated-By: i18nextract.py\n"
        <BLANKLINE>
        #: file1.py:3
        #: file2.py:2
        msgid "msgid1"
        msgstr ""
        <BLANKLINE>
        #: file1.py:5
        msgid "msgid2"
        msgstr ""
        <BLANKLINE>
        <BLANKLINE>

        >>> f.close()
        >>> os.unlink(path)

    """


def setUp(test):
    test.globs['_escapes'] = pygettext.escapes
    pygettext.escapes = []
    pygettext.make_escapes(0)


def tearDown(test):
    pygettext.escapes = test.globs['_escapes']


def test_suite():
    optionflags = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_NDIFF |
                   doctest.REPORT_ONLY_FIRST_FAILURE)
    return unittest.TestSuite([
        doctest.DocTestSuite(optionflags=optionflags,
                             setUp=setUp, tearDown=tearDown),
        doctest.DocTestSuite('schooltool.devtools.i18nextract',
                             optionflags=optionflags),
        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
