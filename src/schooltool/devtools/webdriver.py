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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Selenium runner recipe
"""
import os.path

import selenium.webdriver.remote.webdriver
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.chrome.service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from schooltool.devtools.selenium_recipe import BadOptions


class ChromeWebDriver(selenium.webdriver.chrome.webdriver.WebDriver):
    def __init__(self, executable_path="chromedriver", port=0,
                 desired_capabilities=DesiredCapabilities.CHROME,
                 config=None):
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

        desired_capabilities = dict(desired_capabilities)
        default_prefs = {
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'download.default_directory': config.downloads_dir,
                'translate.enabled': False,
                'profile.password_manager_enabled': False,
                }
        default_prefs.update(desired_capabilities.get('chrome.prefs', {}))
        desired_capabilities['chrome.prefs'] = default_prefs
        options = {'prefs': default_prefs}
        if 'chrome.binary' in desired_capabilities:
            options['binary'] = desired_capabilities['chrome.binary']
        desired_capabilities['chromeOptions'] = options

        selenium.webdriver.remote.webdriver.WebDriver.__init__(
            self,
            command_executor=self.service.service_url,
            desired_capabilities=desired_capabilities)


factory_config_script = '''
%(imports)s
schooltool.devtools.selenium_recipe.factories[%(name)r] =\\
    lambda config=None: %(factory)s(%(args)s)
'''


class python_code(str):
    def __repr__(self):
        return str(self)


def format_args(*args, **kw):
    return ', '.join(([repr(arg) for arg in args] +
                      ['%s=%s' % (i[0], repr(i[1]))
                       for i in sorted(kw.items())]))


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

        kws['desired_capabilities'] = dict(DesiredCapabilities.CHROME)

        arguments = format_args(*args, **kws)

        return self.template % {
            'imports': imps, 'name': driver, 'factory': factory,
            'args': arguments}

    def linux_chrome(self, driver, config):
        imps = 'import schooltool.devtools.webdriver'
        factory = 'schooltool.devtools.webdriver.ChromeWebDriver'
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

        arguments = format_args(*args, **kws)
        arguments = ', '.join([arguments, 'config=config'])

        return self.template % {
            'imports': imps, 'name': driver, 'factory': factory,
            'args': arguments}

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

