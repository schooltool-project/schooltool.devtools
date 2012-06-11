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
import os, sys
import zc.recipe.testrunner
from zope.testrunner.runner import Runner as ZopeTestRunner
import zope.testrunner.feature


factories = {}
default_factory = None
implicit_wait = 30

screenshots_dir = None # Directory to store screenshots
screenshots_url = None # (external) URL to screenshots directory
overwrite_screenshots = False

class SeleniumNotConfigured(Exception):
    pass


class BadOptions(Exception):
    pass


def spawn_browser(factory_name=None):
    if factory_name is None:
        factory_name = default_factory
    if factory_name not in factories:
        if factory_name is None:
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
    '--selenium-headless', action="store_true", dest='selenium_headless',
    help="""\
Run headless, under a virtual display.
""")


selenium_options.add_option(
    '--selenium-headless-backend', action="store", type="string",
    dest='selenium_headless_backend',
    help="""\
Select virtual display backend: xvfb, xvnc, xephyr.
""")

zope.testrunner.options.parser.set_default(
    'selenium_headless_backend', None)

selenium_options.add_option(
    '--selenium-headless-width', action="store", type="int",
    dest='selenium_headless_width')

zope.testrunner.options.parser.set_default(
    'selenium_headless_width', 1024)

selenium_options.add_option(
    '--selenium-headless-height', action="store", type="int",
    dest='selenium_headless_height')

zope.testrunner.options.parser.set_default(
    'selenium_headless_height', 768)

selenium_options.add_option(
    '--selenium-browser', action="store", type="string", dest='selenium_browser',
    help="""\
Specify the browser to run the tests with.
Currently available configurations: %s.
""" % (', '.join(schooltool.devtools.selenium_recipe.factories.keys()) or 'none'))

zope.testrunner.options.parser.set_default(
    'selenium_browser', schooltool.devtools.selenium_recipe.default_factory)

selenium_options.add_option(
    '--selenium-screenshots-dir', action="store", type="string",
    dest='selenium_screenshots_dir',
    help="""\
Store screenshots here.
Directory will be created if not found.
If not specified, no screenshots will be taken.
""")

selenium_options.add_option(
    '--selenium-screenshots-url', action="store", type="string",
    dest='selenium_screenshots_url',
    help="""\
External URL to screenshots directory.  Use file:// if not specified.
""")

selenium_options.add_option(
    '--selenium-overwrite-screenshots', action="store_true", dest='selenium_overwrite',
    help="""\
Overwrite existing files when taking screenshots.
""")

zope.testrunner.options.parser.add_option_group(selenium_options)

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

    virtual_display = None

    @property
    def active(self):
        global factories
        return bool(factories)

    def set_up_virtual_display(self):
        options = self.runner.options

        if (options.selenium_headless or
            options.selenium_headless_backend):
            from pyvirtualdisplay import Display
            self.virtual_display = Display(
                backend=options.selenium_headless_backend,
                visible=False,
                size=(options.selenium_headless_width,
                      options.selenium_headless_height))

    def set_up_screenshots(self):
        options = self.runner.options
        target_dir = options.selenium_screenshots_dir
        if not target_dir:
            if (options.selenium_headless or
                options.selenium_headless_backend):
                # put it somewhere locally by default
                # (like ./parts/*this-testrunner-part*/screenshots)
                target_dir = 'screenshots'
            else:
                return

        global overwrite_screenshots
        overwrite_screenshots = options.selenium_overwrite

        global screenshots_dir
        global screenshots_url

        screenshots_dir = os.path.normpath(target_dir)

        if not os.path.exists(screenshots_dir):
            os.mkdir(screenshots_dir)

        if options.selenium_screenshots_url:
            screenshots_url = options.selenium_screenshots_url
            if not screenshots_url.endswith('/'):
                screenshots_url += '/'


    def global_setup(self):
        options = self.runner.options

        global default_factory
        default_factory = options.selenium_browser

        self.set_up_virtual_display()
        self.set_up_screenshots()

    def layer_setup(self, layer):
        if self.virtual_display:
            self.virtual_display.start()

    def layer_teardown(self, layer):
        if self.virtual_display:
            self.virtual_display.stop()


class Runner(ZopeTestRunner):

    def configure(self):
        ZopeTestRunner.configure(self)
        selenium = RunnerSeleniumFeature(self)
        if selenium.active:
            self.features.append(selenium)

