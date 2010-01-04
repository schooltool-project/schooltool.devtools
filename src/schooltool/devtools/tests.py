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

import unittest
import os
from cStringIO import StringIO

from zope.app.locales import pygettext
from zope.testing import doctest
from zope.i18nmessageid import Message


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
