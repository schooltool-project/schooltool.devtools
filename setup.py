#!/usr/bin/env python
#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2007,2008,2009    Shuttleworth Foundation,
#                                 Ignas Mikalajunas
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
SchoolTool DevTools setup script
"""

import os
from setuptools import setup, find_packages

if os.path.exists("version.txt"):
    version = open("version.txt").read().strip()
else:
    version = open("version.txt.in").read().strip()

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return text

setup(
    name="schooltool.devtools",
    description="SchoolTool development tools.",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    version=version,
    url='http://www.schooltool.org',
    license="GPL",
    maintainer="SchoolTool Developers",
    maintainer_email="schooltool-developers@lists.launchpad.net",
    platforms=["any"],
    classifiers=["Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Zope"],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=["schooltool"],
    install_requires=['zope.testing',
                      'zope.app.locales',
                      'setuptools'],
    entry_points="""
    [console_scripts]
    i18nextract = schooltool.devtools.i18nextract:i18nextract
    runfdoctests = schooltool.devtools.runfdoctests:main
    """,
    include_package_data=True,
    zip_safe=False,
    )
