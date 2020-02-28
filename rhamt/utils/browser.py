from urllib.error import URLError

from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import WebDriverException
from werkzeug.local import LocalProxy

from rhamt.utils import conf
from rhamt.utils import tries


class BrowserFactory(object):
    def __init__(self, webdriver_class, browser_kwargs):
        self.webdriver_class = webdriver_class
        self.browser_kwargs = browser_kwargs

    def create(self, url_key):
        try:
            browser = tries(
                2, WebDriverException,
                self.webdriver_class, **self.browser_kwargs())
        except URLError as e:
                raise RuntimeError('Could not connect to Selenium server. Is it up and running?')

        browser.maximize_window()
        browser.get(url_key)
        browser.url_key = url_key
        return browser

    def close(self, browser):
        if browser:
            browser.quit()


class BrowserManager(object):
    def __init__(self, browser_factory):
        self.factory = browser_factory
        self.browser = None
        self._browser_renew_thread = None

    def coerce_url_key(self, key):
        return key

    @classmethod
    def from_conf(cls, browser_conf):
        webdriver_name = browser_conf.get('webdriver', 'Firefox')
        webdriver_class = getattr(webdriver, webdriver_name)

        browser_kwargs = browser_conf.get('webdriver_options', {})
        if webdriver_name.lower() == "remote":
            if browser_conf[
                    'webdriver_options'][
                        'desired_capabilities']['browserName'].lower() == 'chrome':
                browser_kwargs['desired_capabilities']['chromeOptions'] = {}
                browser_kwargs[
                    'desired_capabilities']['chromeOptions']['args'] = ['--no-sandbox',
                                                                        '--start-maximized',
                                                                        '--disable-extensions',
                                                                        'disable-infobars']
                browser_kwargs['desired_capabilities'].pop('marionette', None)
        return cls(BrowserFactory(webdriver_class, browser_kwargs))

    def _is_alive(self):
        # log.debug("alive check")
        try:
            self.browser.current_url
        except UnexpectedAlertPresentException:
            # We shouldn't think that an Unexpected alert means the browser is dead
            return True
        except Exception:
            # log.exception("browser in unknown state, considering dead")
            return False
        return True

    def ensure_open(self, url_key=None):
        url_key = self.coerce_url_key(url_key)
        if getattr(self.browser, 'url_key', None) != url_key:
            return self.start(url_key=url_key)

        if self._is_alive():
            return self.browser
        else:
            return self.start(url_key=url_key)

    def add_cleanup(self, callback):
        assert self.browser is not None
        try:
            cl = self.browser.__cleanup
        except AttributeError:
            cl = self.browser.__cleanup = []
        cl.append(callback)

    def _consume_cleanups(self):
        try:
            cl = self.browser.__cleanup
        except AttributeError:
            pass
        else:
            while cl:
                cl.pop()()

    def quit(self):
        # TODO: figure if we want to log the url key here
        self._consume_cleanups()
        try:
            self.factory.close(self.browser)
        except Exception as e:
            # log.error('An exception happened during browser shutdown:')
            # log.exception(e)
            raise
        finally:
            self.browser = None

    def start(self, url_key=None):
        # log.info('starting browser')
        url_key = self.coerce_url_key(url_key)
        if self.browser is not None:
            self.quit()
        return self.open_fresh(url_key=url_key)

    def open_fresh(self, url_key=None):
        url_key = self.coerce_url_key(url_key)
        # log.info('starting browser for %r', url_key)
        assert self.browser is None

        self.browser = self.factory.create(url_key=url_key)
        return self.browser


manager = BrowserManager.from_conf(conf.env.get('browser', {}))
driver = LocalProxy(manager.ensure_open)