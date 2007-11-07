#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2005 Shuttleworth Foundation
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
Customization of Zope's message string extraction module for schooltool and
schoolbell.

$Id$
"""
import os
import sys
import optparse
import pkg_resources

from zope.app.locales.extract import py_strings

_import_chickens = {}, {}, ("*",) # dead chickens needed by __import__

here = os.path.abspath(os.path.dirname(__file__))

from zope.app.locales import extract
# Monkey patch the Zope3 translation extraction machinery
extract.pot_header = """\
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
"Project-Id-Version: %(version)s\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: Schooltool Development Team <schooltool-dev@schooltool.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=%(charset)s\\n"
"Content-Transfer-Encoding: %(encoding)s\\n"
"Generated-By: i18nextract.py\\n"

"""

version = "SVN"
class POTMaker(extract.POTMaker):

    def _getProductVersion(self):
        return "SchoolTool Version %s" % version


def write_pot(output_file, path, domain, base_dir, site_zcml):
    # Create the POT
    maker = POTMaker(output_file, path)
    maker.add(py_strings(path, domain, verify_domain=True), base_dir)
    maker.add(extract.zcml_strings(path, domain, site_zcml=site_zcml), base_dir)
    maker.add(extract.tal_strings(path, domain), base_dir)
    maker.write()

def parse_args(argv):
    """Parse the command line arguments"""
    parser = optparse.OptionParser(usage="usage: %prog [options]")
    # XXX ! separate these
    parser.add_option("--egg", dest="egg", default="schooltool",
                      help="The egg that contains files to be extracted")
    parser.add_option("--domain", dest="domain", default=None,
                      help="The domain that should be extracted")
    parser.add_option("--zcml", dest="zcml", default=None,
                      help="ZCML file to start the extraction")
    parser.add_option("--output-file", dest="output_file", default=None,
                      help="Locales directory to store the pot file")
    options, args = parser.parse_args(argv)
    assert len(args) == 1
    assert options.domain is not None
    assert options.zcml is not None
    assert options.output_file is not None
    assert options.egg is not None
    return options


def i18nextract():
    here = os.path.abspath(os.path.curdir)
    options = parse_args(sys.argv)
    path = list(pkg_resources.require(options.egg))[0].location
    base_dir = os.path.abspath(os.path.join(path, ".."))
    output_file = os.path.abspath(options.output_file)
    zcml_path = os.path.join(path, options.zcml)
    write_pot(output_file, path, options.domain, base_dir, zcml_path)
    print 'Extracted %s' % output_file