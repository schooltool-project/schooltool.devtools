#!/usr/bin/env python
#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2005    Shuttleworth Foundation,
#                       Brian Sutherland
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
SchoolTool Lyceum plugin setup script.
"""


# Check python version
import sys
if sys.version_info < (2, 4):
    print >> sys.stderr, '%s: need Python 2.4 or later.' % sys.argv[0]
    print >> sys.stderr, 'Your python is %s' % sys.version
    sys.exit(1)

import os
from setuptools import setup, find_packages

# Setup STDevTools
setup(
    name="schooltool.devtools",
    description="SchoolTool development tools.",
    long_description="""A set of tools that helps when developing schooltool.
    Like html coverage report generation scripts, i18n information extraction
    utilites and etc.""",
    version="0.3dev",
    url='http://www.schooltool.org',
    license="GPL",
    maintainer="SchoolTool development team",
    maintainer_email="schooltool-dev@schooltool.org",
    platforms=["any"],
    classifiers=["Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Zope"],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=['zope.testing',
                      'zope.app.locales',
                      'setuptools'],
    entry_points="""
    [console_scripts]
    i18nextract = schooltool.devtools.i18nextract:i18nextract
    coverage_reports = schooltool.devtools.coverage_reports:main
    runfdoctests = schooltool.devtools.runfdoctests:main
    """,
    include_package_data=True)
