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
"""
import os
import sys
import time
import optparse
import pkg_resources

_import_chickens = {}, {}, ("*",) # dead chickens needed by __import__

here = os.path.abspath(os.path.dirname(__file__))

from zope.app.locales import extract

pot_header = """\
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
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: i18nextract.py\\n"

"""


class STPOTEntry(extract.POTEntry):
    pass


class STPOTMaker(extract.POTMaker):

    def __init__ (self, output_fn, path, domain=None):
        super(STPOTMaker, self).__init__(output_fn, path)
        self.domain = domain

    def _getProductVersion(self):
        return self.domain

    def write(self):
        "Overriden to write date in the correct format"
        file = open(self._output_filename, 'w')
        ztime = time.strftime('%Y-%m-%d %H:%M%z')
        file.write(pot_header % {'time':     ztime,
                                 'version':  self._getProductVersion()})

        # Sort the catalog entries by filename
        catalog = self.catalog.values()
        catalog.sort()

        # Write each entry to the file
        for entry in catalog:
            entry.write(file)

        file.close()


def write_pot(output_file, eggs, domain, site_zcml):
    maker = STPOTMaker(output_file, here, domain=domain)
    catalog = {}
    for egg in eggs:
        src_path = list(pkg_resources.require(egg))[0].location
        # XXX: temporary egg/zcml base dir consistency hack
        base_dir = src_path
        if os.path.basename(base_dir) == 'src':
            base_dir = os.path.split(base_dir)[0]
        first_module = egg.split('.')[0]
        path = os.path.join(src_path, first_module)
        maker.add(extract.py_strings(path, domain, verify_domain=True),
            base_dir)
        maker.add(extract.tal_strings(path, domain),
            base_dir)
    if site_zcml is not None:
        base_dir = os.getcwd()
        maker.add(extract.zcml_strings(base_dir, domain, site_zcml=site_zcml),
            base_dir)
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
