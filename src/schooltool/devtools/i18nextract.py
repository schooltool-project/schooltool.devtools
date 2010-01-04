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
Customization of Zope's message string extraction module for SchoolTool

$Id$
"""
import os
import sys
import optparse
import pkg_resources

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


class STPOTEntry(extract.POTEntry):

    def __init__(self, *args, **kw):
        super(STPOTEntry, self).__init__(*args, **kw)
        self._locations = []

    def addLocationComment(self, filename, line):
        self._locations.append((filename, line))
        super(STPOTEntry, self).addLocationComment(filename, line)

    def __cmp__(self, other):
        return cmp((self._locations, self.msgid),
                   (other._locations, other.msgid))


version = "development"
class STPOTMaker(extract.POTMaker):

    def _getProductVersion(self):
        return "SchoolTool %s" % version

    def add(self, strings, base_dir=None):
        for msgid, locations in strings.items():
            if msgid == '':
                continue
            if msgid not in self.catalog:
                self.catalog[msgid] = STPOTEntry(msgid)

            for filename, lineno in locations:
                if base_dir is not None:
                    filename = filename.replace(base_dir, '')
                self.catalog[msgid].addLocationComment(filename, lineno)


def update_catalog(strings, other, location_prefix=None):
    for msg, locations in other.items():
        if location_prefix:
            locations = [
                (filename.replace(location_prefix, ''), lineno)
                for filename, lineno in locations]
        if msg not in strings:
            strings[msg] = sorted(locations)
        else:
            strings[msg] = sorted(set(strings[msg] + locations))


def write_pot(output_file, eggs, domain, site_zcml):
    maker = STPOTMaker(output_file, here)
    catalog = {}
    for egg in eggs:
        src_path = list(pkg_resources.require(egg))[0].location
        # XXX: temporary egg/zcml base dir consistency hack
        base_dir = src_path
        if os.path.basename(base_dir) == 'src':
            base_dir = os.path.split(base_dir)[0]
        first_module = egg.split('.')[0]
        path = os.path.join(src_path, first_module)
        update_catalog(
            catalog, extract.py_strings(path, domain, verify_domain=True),
            location_prefix=base_dir)
        update_catalog(
            catalog, extract.tal_strings(path, domain),
            location_prefix=base_dir)
    if site_zcml is not None:
        base_dir = os.getcwd()
        update_catalog(
            catalog, extract.zcml_strings(base_dir, domain, site_zcml=site_zcml),
            location_prefix=base_dir)
    maker.add(catalog)
    maker.write()


def parse_args(argv):
    """Parse the command line arguments"""
    parser = optparse.OptionParser(usage="usage: %prog [options]")
    # XXX ! separate these
    parser.add_option("--egg", dest="egg", default=[], action="append",
                      help="The egg that contains files to be extracted")
    parser.add_option("--domain", dest="domain", default=None,
                      help="The domain that should be extracted")
    parser.add_option("--zcml-egg", dest="zcml_egg", default=None,
                      help="Egg that contains the ZCML")
    parser.add_option("--zcml", dest="zcml", default=None,
                      help="ZCML file to start the extraction")
    parser.add_option("--output-file", dest="output_file", default=None,
                      help="Locales directory to store the pot file")
    options, args = parser.parse_args(argv)
    assert len(args) == 1
    assert options.domain is not None
    assert options.output_file is not None
    assert options.egg is not None
    if options.zcml:
        if options.zcml_egg is None and len(options.egg) == 1:
            options.zcml_egg = options.egg[0]
        else:
            assert options.zcml_egg is not None
    return options


def i18nextract():
    here = os.path.abspath(os.path.curdir)
    options = parse_args(sys.argv)
    output_file = os.path.abspath(options.output_file)
    site_zcml = None
    if options.zcml:
        zcml_path = list(pkg_resources.require(options.zcml_egg))[0].location
        site_zcml = os.path.join(zcml_path, options.zcml)
    write_pot(output_file, options.egg, options.domain, site_zcml)
    print 'Extracted %s' % output_file
