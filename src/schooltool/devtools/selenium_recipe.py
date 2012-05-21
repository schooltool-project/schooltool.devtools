#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2011 Shuttleworth Foundation
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
Selenium runner recipe
----------------------

To use the selenium testrunner, add a section to buildout.cfg::

  [test-selenium]
  recipe = schooltool.devtools:testrunner
  eggs = ${package:eggs}
  defaults = ['--tests-pattern', '^s?tests$']

  # To run selenium tests:
  # - Download standalone selenium server from
  #     http://code.google.com/p/selenium/downloads/list
  # - Start the server: "java -jar selenium-server-standalone-2.6.0.jar"
  # - Uncomment the lines below:
  #
  #selenium.default = html_unit
  #selenium.html_unit.web_driver = remote
  #selenium.html_unit.capabilities = HTMLUNITWITHJS

"""
import sys
import zc.recipe.testrunner
from zope.testrunner.runner import Runner as ZopeTestRunner
import zope.testrunner.feature


factories = {}
default_factory = None
implicit_wait = 30


class SeleniumNotConfigured(Exception):
    pass


class BadOptions(Exception):
    pass


def spawn_browser(factory_name=None):
    if factory_name is None:
        factory_name = default_factory
    if factory_name not in factories:
        if factory_name == default_factory:
            raise SeleniumNotConfigured(
                "Default selenium web driver not configured.")
        raise SeleniumNotConfigured(
            "Web driver %r not configured." % factory_name)
    browser = factories[factory_name]()
    browser.implicitly_wait(implicit_wait)
    return browser


def eval_val(val):
    try:
        return eval(val)
    except:
        return val


def unflatten_options(options, prefix="", value_parser=eval_val):
    result = {}
    if prefix:
        prefix += "."
    for key in sorted(options.keys()):
        if prefix and not key.startswith(prefix):
            continue
        names = key[len(prefix):].split('.')
        target = result
        for n, name in enumerate(names[:-1]):
            if name not in target:
                target[name] = {}
            elif not isinstance(target[name], dict):
                raise BadOptions(
                    "Cannot set %s, %s is already %r" % (
                        '.'.join(names),
                        '.'.join(names[:n+1]),
                        target[name]))
            target = target[name]
        target[names[-1]] = value_parser(options[key])
    return result


selenium_config_script = '''
import schooltool.devtools.selenium_recipe
schooltool.devtools.selenium_recipe.default_factory = %(default_factory)r
%(factory_templates)s
%(selenium_options)s
'''


selenium_options_script = '''
import schooltool.devtools.selenium_recipe

import optparse
import zope.testrunner.options
import zope.testrunner.runner

selenium_options = optparse.OptionGroup(
    zope.testrunner.options.parser,
    "Selenium", """\
Additional options for Selenium tests.
""")

selenium_options.add_option(
    '--selenium-browser', action="store", type="string", dest='selenium_browser',
    help="""\
Specify the browser to run the tests with.
Available configurations: %s.
""" % (', '.join(schooltool.devtools.selenium_recipe.factories.keys()) or 'none'))

zope.testrunner.options.parser.add_option_group(selenium_options)
zope.testrunner.options.parser.set_default(
    'selenium_browser', schooltool.devtools.selenium_recipe.default_factory)

# Replace the default Zope test runner
zope.testrunner.runner.Runner = schooltool.devtools.selenium_recipe.Runner
'''


class SeleniumRunnerRecipe(zc.recipe.testrunner.TestRunner):

    def __init__(self, buildout, name, options):
        zc.recipe.testrunner.TestRunner.__init__(self, buildout, name, options)
        selenium_init = self.getSeleniumSection(options)
        extra_init = options.get('initialization', '').strip()
        options['initialization'] = '%s\n\n%s' % (selenium_init, extra_init)

    def getSeleniumSection(self, options):
        driver_configs = unflatten_options(options, "selenium")
        if not driver_configs:
            return ''
        default_driver = driver_configs.pop('default', None)
        if default_driver and default_driver not in driver_configs:
            raise BadOptions('No configuration for default driver'
                             'selenium.%s' % default_driver)

        try:
            from schooltool.devtools.webdriver import ScriptFactory
            script_factory = ScriptFactory()
        except SyntaxError:
            print >> sys.stderr, 'warning: selenium is not compatible with python << 2.6'
            return ''

        scripts = []

        implicit_wait = driver_configs.pop('implicit_wait', None)
        if implicit_wait:
            scripts.append(
                'schooltool.devtools.selenium_recipe.implicit_wait = %f' % (
                    float(implicit_wait)))

        for driver, config in sorted(driver_configs.items()):
            if (not isinstance(config, dict) and
                config != "default"):
                raise BadOptions(
                    'Driver %r config must be a dict in form of'
                    ' "mydriver.setting = ..." or "mydriver=default"'
                    ' for standard WebDrivers, not'
                    ' %r' % (driver, config))
            if config == "default":
                scripts.append(script_factory(driver, {}))
            else:
                scripts.append(script_factory(driver, config))

        return selenium_config_script % {
            'default_factory': default_driver,
            'factory_templates': '\n\n'.join(scripts),
            'selenium_options': selenium_options_script,
            }


class RunnerSeleniumFeature(zope.testrunner.feature.Feature):

    @property
    def active(self):
        global factories
        return bool(factories)

    def global_setup(self):
        global default_factory
        default_factory = self.runner.options.selenium_browser


class Runner(ZopeTestRunner):

    def configure(self):
        ZopeTestRunner.configure(self)
        selenium = RunnerSeleniumFeature(self)
        if selenium.active:
            self.features.append(selenium)

