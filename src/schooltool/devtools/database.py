#!/usr/bin/env python
#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2013 Shuttleworth Foundation
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Helpers to interactively hack SchoolTool db.
"""
import errno
import os
import optparse
import readline
import sys
import ZConfig

from zope.app.publication.zopepublication import ZopePublication
from zope.component import provideUtility
from ZODB.interfaces import IDatabase
from ZODB.ActivityMonitor import ActivityMonitor
from zope.site.hooks import getSite, setSite

from schooltool.app.main import SchoolToolMachinery


class Machinery(SchoolToolMachinery):

    def load_options(self, argv):
        parser = optparse.OptionParser(usage="usage: %prog [options]")
        parser.add_option("--config", dest="config_file", default='instance/schooltool.conf',
                          help="Path to schooltool.conf or point to ST config itself")
        options, args = parser.parse_args(argv)
        assert os.path.exists(options.config_file)
        if os.path.isdir(options.config_file):
            options.config_file = os.path.join(options.config_file, 'schooltool.conf')

        print "Reading configuration from %s" % options.config_file
        progname = os.path.basename(argv[0])
        try:
            options.config, handler = self.readConfig(options.config_file)
        except ZConfig.ConfigurationError, e:
            print >> sys.stderr, "%s: %s" % (progname, e)
            sys.exit(1)
        if options.config.database.config.storage is None:
            print >> sys.stderr, "%s: %s" % (progname,
                "No storage defined in the configuration file.")
            sys.exit(1)
        return options

    def openDB(self, options):
        # Open the database
        db_configuration = options.config.database
        try:
            db = db_configuration.open()
        except IOError, e:
            print >> sys.stderr, "Could not initialize the database:\n%s" % e
            if e.errno == errno.EAGAIN: # Resource temporarily unavailable
                print >> sys.stderr, "\nPerhaps another %s instance" \
                                     " is using it?" % self.system_name
            sys.exit(1)
        provideUtility(db, IDatabase)
        db.setActivityMonitor(ActivityMonitor())
        return db


def interact(machinery, database, shell):
    try:
        connection = database.open()
        root = connection.root()
        app = root[ZopePublication.root_name]
        oldsite = getSite()
        setSite(app)
        scope = {
            'machinery': machinery,
            'database': database,
            'connection': connection,
            'root': root,
            'app': app,
            }
        shell(scope)
    finally:
        e = None
        try:
            setSite(oldsite)
        except Exception, e:
            pass
        try:
            connection.close()
        except Exception, e:
            pass
        database.close()
        if e is not None:
            raise e


def python_shell(scope):
    __import__("code").interact(banner="", local=scope)


def ipython_shell(scope):
    from IPython.frontend.terminal.embed import InteractiveShellEmbed
    from IPython.config.loader import Config
    cfg = Config()
    shell = InteractiveShellEmbed(config=cfg)
    sys.exit(shell(local_ns=scope))

shell = python_shell

try:
    import IPython
    shell = ipython_shell
except ImportError:
    pass


def open_database(config="instance/schooltool.conf", with_components=True):
    machinery = Machinery()
    options = machinery.load_options([sys.argv[0], '--config', config])
    if with_components:
        machinery.configure(options)
    database = machinery.openDB(options)
    return database


def open_pure_database(config="instance/schooltool.conf"):
    return open_database(config=config, with_components=False)


def main():
    # Tab completion
    readline.set_completer_delims(' \t\n')
    readline.parse_and_bind('tab: complete')

    machinery = Machinery()
    options = machinery.load_options(sys.argv)
    machinery.configure(options)
    database = machinery.openDB(options)
    global shell
    interact(machinery, database, shell)
