#!/usr/bin/env python
#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2007-2013 Shuttleworth Foundation
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
    description="SchoolTool Devtools",
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
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Zope",
    "Topic :: Education"],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=["schooltool"],
    install_requires=['zope.testrunner',
                      'zope.app.locales >= 3.7.2',
                      'zc.recipe.testrunner',
                      'selenium',
                      'PyVirtualDisplay',
                      'setuptools'],
    entry_points="""
    [zc.buildout]
    testrunner = schooltool.devtools.selenium_recipe:SeleniumRunnerRecipe

    [console_scripts]
    i18nextract = schooltool.devtools.i18nextract:i18nextract
    runfdoctests = schooltool.devtools.runfdoctests:main
    debugdb = schooltool.devtools.database:main
    """,
    include_package_data=True,
    zip_safe=False,
    )
