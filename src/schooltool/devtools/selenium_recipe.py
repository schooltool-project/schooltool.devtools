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
Selenium driver config.
"""
import os.path

import zc.recipe.testrunner
import selenium.webdriver.remote.webdriver
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.chrome.service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


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


factory_config_script = '''
%(imports)s
schooltool.devtools.selenium_recipe.factories[%(name)r] =\\
    lambda: %(factory)s(%(args)s)
'''


class python_code(str):
    def __repr__(self):
        return str(self)


def format_args(*args, **kw):
    return ', '.join(([repr(arg) for arg in args] +
                      ['%s=%s' % (i[0], repr(i[1]))
                       for i in sorted(kw.items())]))


class ChromeWebDriver(selenium.webdriver.chrome.webdriver.WebDriver):
    def __init__(self, executable_path="chromedriver", port=0,
                 desired_capabilities=DesiredCapabilities.CHROME):
        """ Creates a new instance of the chrome driver. Starts the service
            and then creates
            Attributes:
                executable_path : path to the executable. If the default
                    is used it assumes the executable is in the $PATH
                port : port you would like the service to run, if left
                    as 0, a free port will be found

        """
        self.service = selenium.webdriver.chrome.service.Service(
            executable_path, port=port)
        self.service.start()

        selenium.webdriver.remote.webdriver.WebDriver.__init__(
            self,
            command_executor=self.service.service_url,
            desired_capabilities=desired_capabilities)


class ScriptFactory(object):

    template = factory_config_script

    def firefox(self, driver, config):
        imps = 'import selenium.webdriver.firefox.webdriver'
        factory = 'selenium.webdriver.firefox.webdriver.WebDriver'
        args = []
        kws = {}

        if 'timeout' in config:
            kws['timeout'] = int(config['timeout'])

        if 'profile' in config:
            imps += ('\nfrom selenium.webdriver.firefox.firefox_profile' +
                     ' import FirefoxProfile')
            kws['firefox_profile'] = python_code('FirefoxProfile(%s)' % (
                format_args(os.path.abspath(config['profile']))))

        if 'binary' in config:
            imps += ('\nfrom selenium.webdriver.firefox.firefox_binary' +
                     ' import FirefoxBinary')
            kws['firefox_binary'] = python_code('FirefoxBinary(%s)' % (
                format_args(os.path.abspath(config['binary']))))

        return self.template % {
            'imports': imps, 'name': driver, 'factory': factory,
            'factory': factory,
            'args': format_args(*args, **kws)}

    def ie(self, driver, config):
        imps = 'import selenium.webdriver.ie.webdriver'
        factory = 'selenium.webdriver.ie.webdriver.WebDriver'
        args = []
        kws = {}

        if 'port' in config:
            kws['port'] = int(config['port'])
        if 'timeout' in config:
            kws['timeout'] = int(config['timeout'])
        return self.template % {
            'imports': imps, 'name': driver, 'factory': factory,
            'args': format_args(*args, **kws)}

    def chrome(self, driver, config):
        imps = 'import selenium.webdriver.chrome.webdriver'
        factory = 'selenium.webdriver.chrome.webdriver.WebDriver'
        args = []
        kws = {}

        if 'port' in config:
            kws['port'] = int(config['port'])
        if 'binary' in config:
            kws['executable_path'] = config['binary']

        if 'binary' in config:
            kws['executable_path'] = config['binary']

        return self.template % {
            'imports': imps, 'name': driver, 'factory': factory,
            'args': format_args(*args, **kws)}

    def linux_chrome(self, driver, config):
        imps = 'import schooltool.devtools.selenium_recipe'
        factory = 'schooltool.devtools.selenium_recipe.ChromeWebDriver'
        args = []
        kws = {}

        if 'port' in config:
            kws['port'] = int(config['port'])
        if 'binary' in config:
            kws['executable_path'] = config['binary']

        if 'capabilities' in config:
            assert isinstance(config['capabilities'], dict)
            caps = dict(config['capabilities'])
            if ('chrome' in caps and
                'binary' in caps['chrome']):
                caps['chrome.binary'] = caps['chrome']['binary']
                del caps['chrome']['binary']
                if not caps['chrome']:
                    del caps['chrome']
            kws['desired_capabilities'] = dict(DesiredCapabilities.CHROME)
            kws['desired_capabilities'].update(caps)

        return self.template % {
            'imports': imps, 'name': driver, 'factory': factory,
            'args': format_args(*args, **kws)}

    def remote(self, driver, config):
        imps = 'import selenium.webdriver.remote.webdriver'
        factory = 'selenium.webdriver.remote.webdriver.WebDriver'
        args = []
        kws = {}

        if 'remote_hub' in config:
            kws['command_executor'] = config['remote_hub']

        if 'capabilities' not in config:
            raise BadOptions(
                'Must set "capabilities" for remote WebDriver %r' % driver)

        capabilities = config['capabilities']
        if isinstance(capabilities, str):
            capabilities = capabilities.upper().strip()
            if capabilities in DesiredCapabilities.__dict__:
                capabilities = dict(getattr(DesiredCapabilities, capabilities))
            else:
                available = sorted([c for c in DesiredCapabilities.__dict__
                                    if not c.startswith('__')])
                raise BadOptions(
                    '"capabilities" for %r should be custom or one of: %s.' % (
                    driver, ', '.join(available)))
        elif not isinstance(capabilities, dict):
            raise BadOptions(
                '"capabilities" for %r must be a dic' % driver)

        kws['desired_capabilities'] = capabilities

        if 'profile' in config:
            imps += ('\nfrom selenium.webdriver.firefox.firefox_profile' +
                     ' import FirefoxProfile')
            kws['browser_profile'] = 'FirefoxProfile(%r)' % (
                os.path.abspath(config['profile']))

        return self.template % {
            'imports': imps, 'name': driver, 'factory': factory,
            'args': format_args(*args, **kws)}

    def __call__(self, driver, config):
        handler = config.get('web_driver', driver.lower())
        try:
            script_maker = getattr(self, handler)
        except AttributeError:
            raise BadOptions('Need to specify selenium webdriver'
                             ' (selenium.%s.web_driver)'
                             ' for %r ' % (driver, driver))
        return script_maker(driver, config)


selenium_config_script = '''
import schooltool.devtools.selenium_recipe
schooltool.devtools.selenium_recipe.default_factory = %(default_factory)r
%(factory_templates)s
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

        script_factory = ScriptFactory()

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
            }
