# -*- coding: utf-8 -*-
import os
import time
from copy import copy
from inspect import isclass

from cached_property import cached_property
from selenium.common.exceptions import NoSuchElementException
from taretto.navigate import Navigate
from taretto.navigate import NavigateStep
from taretto.navigate import NavigationTriesExceeded
from taretto.ui import Browser
from taretto.ui import DefaultPlugin
from wait_for import wait_for
from webdriver_kaifuku import BrowserManager

from . import Implementation
from . import MTAImplementationContext
from mta.utils.log import logger


class MTABrowserPlugin(DefaultPlugin):
    # TODO: Need to add proper `ENSURE_PAGE_SAFE` js script as per observations
    DEFAULT_WAIT = 0.8

    def ensure_page_safe(self, timeout="20s"):
        # THIS ONE SHOULD ALWAYS USE JAVASCRIPT ONLY, NO OTHER SELENIUM INTERACTION
        def _check():
            page_safe = self.browser.execute_script(self.ENSURE_PAGE_SAFE)
            self.browser.logger.debug("page_safe is %s", not page_safe)
            return page_safe

        wait_for(_check, timeout=timeout, delay=0.2, silent_failure=True, very_quiet=True)

    def after_keyboard_input(self, element, keyboard_input):
        self.browser.plugin.ensure_page_safe()

    def after_click(self, element, locator):
        # page_dirty is set to None because otherwise if it was true, all next ensure_page_safe
        # calls would check alert presence which is enormously slow in selenium.
        self.browser.page_dirty = None


class MTABrowser(Browser):
    def __init__(self, selenium_webdriver, endpoint, extra_objects=None):
        extra_objects = extra_objects or {}
        extra_objects.update({"application": endpoint.owner, "endpoint": endpoint})
        super(MTABrowser, self).__init__(
            selenium_webdriver,
            plugin_class=MTABrowserPlugin,
            logger=logger,
            extra_objects=extra_objects,
        )
        self.window_handle = selenium_webdriver.current_window_handle
        self.logger.info(
            "Opened browser %s %s",
            selenium_webdriver.capabilities.get("browserName", "unknown"),
            selenium_webdriver.capabilities.get("version", "unknown"),
        )

    @property
    def application(self):
        return self.extra_objects["application"]

    def create_view(self, *args, **kwargs):
        return self.application.operator_ui.create_view(*args, **kwargs)

    @property
    def product_version(self):
        return self.application.version


def can_skip_pre_nav_prep(fn):
    """Decorator for setting a noop"""
    fn._can_skip_pre_nav_prep = True
    return fn


class NavigatableMixin(object):
    """NavigatableMixin ensures that an object can navigate properly

    The NavigatableMixin object ensures that a Collection/Entity object inside the
    framework has access to be able to **create** a Widgetastic View, and that it
    has access to the browser.

    Note: The browser access will have to change once proliferation of the Sentaku
          system becomes common place
    """

    @property
    def browser(self):
        return self.application.operator_ui.widgetastic_browser

    def create_view(self, view_class, o=None, override=None):
        o = o or self
        if override is not None:
            new_obj = copy(o)
            new_obj.__dict__.update(override)
        else:
            new_obj = o
        return self.application.operator_ui.create_view(
            view_class, additional_context={"object": new_obj}
        )

    def list_destinations(self):
        """This function returns a list of all valid destinations for a particular object
        """
        return {
            impl.name: impl.navigator.list_destinations(self)
            for impl in self.application.context.implementations.values()
            if impl.navigator
        }


class MTANavigateStep(NavigateStep):
    VIEW = None

    @cached_property
    def view(self):
        if self.VIEW is None:
            raise AttributeError(f"{type(self).__name__} does not have VIEW specified")
        return self.create_view(self.VIEW, additional_context={"object": self.obj})

    @property
    def application(self):
        return self.obj.application

    def create_view(self, *args, **kwargs):
        return self.application.operator_ui.create_view(*args, **kwargs)

    def am_i_here(self):
        try:
            return self.view.is_displayed
        except (AttributeError, NoSuchElementException):
            return False

    def pre_nav_prep(self, fn, _tries, nav_args, *args, **kwargs):
        go_kwargs = kwargs.copy()
        go_kwargs.update(nav_args)
        self.log_message(f"Invoking {fn.__name__}, with {args} and {kwargs}", level="debug")

        # TODO: Add pre nav checks to improve UI experience
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self.log_message(f"pre_nav_prep hit Exception: {e}", level="warning")
            self.go(_tries, *args, **go_kwargs)

    @can_skip_pre_nav_prep
    def resetter(self, *args, **kwargs):
        pass

    @can_skip_pre_nav_prep
    def pre_navigate(self, *args, **kwargs):
        pass

    @can_skip_pre_nav_prep
    def post_navigate(self, *args, **kwargs):
        pass

    @property
    def _obj_name(self):
        return self.obj.__name__ if isclass(self.obj) else self.obj.__class__.__name__

    def log_message(self, msg, level="debug"):
        str_msg = "[UI-NAV/{}/{}]: {}".format(self._obj_name, self._name, msg)  # Legitimate old use
        getattr(logger, level)(str_msg)

    def construct_message(self, here, resetter, view, duration, waited):
        str_here = "Already Here" if here else "Needed Navigation"
        str_resetter = "Resetter Used" if resetter else "No Resetter"
        str_view = "View Returned" if view else "No View Available"
        str_waited = "Waited on View" if waited else "No Wait on View"
        return f"{str_here}/{str_resetter}/{str_view}/{str_waited} (elapsed {duration}ms)"

    def go(self, _tries=0, *args, **kwargs):
        nav_args = {"use_resetter": True, "wait_for_view": False}
        self.log_message(f"Beginning Navigation (tries={_tries})", level="info")
        start_time = time.time()
        if _tries > 2:
            # Need at least three tries:
            # 1: login_admin handles an alert or CannotContinueWithNavigation appears.
            # 2: Everything should work. If not, NavigationError.
            raise NavigationTriesExceeded(f'{self._obj_name}, "{self._name}"')

        _tries += 1
        for arg in nav_args:
            if arg in kwargs:
                nav_args[arg] = kwargs.pop(arg)

        self.pre_nav_prep(self.pre_navigate, _tries, nav_args, *args, **kwargs)

        here = False
        resetter_used = False
        waited = False

        try:
            # Testing out not wrapping the am_i_here call in the pre nav prep
            here = self.am_i_here()
        except Exception as e:
            self.log_message(f"Hit an exception {e} with am I here - assuming False")

        if not here:
            self.log_message("Prerequisite Needed")
            self.prerequisite_view = self.prerequisite()
            self.pre_nav_prep(self.step, _tries, nav_args, *args, **kwargs)

        if nav_args["use_resetter"]:
            resetter_used = True
            self.pre_nav_prep(self.resetter, _tries, nav_args, *args, **kwargs)

        self.pre_nav_prep(self.post_navigate, _tries, nav_args, *args, **kwargs)
        view = self.view if self.VIEW is not None else None
        duration = int((time.time() - start_time) * 1000)
        if (
            view
            and nav_args["wait_for_view"]
            and not os.environ.get("DISABLE_NAVIGATE_ASSERT", False)
        ):
            waited = True
            wait_for(
                lambda: view.is_displayed,
                num_sec=10,
                message=f"Waiting for view [{view.__class__.__name__}] to display",
            )
        self.log_message(
            self.construct_message(here, resetter_used, view, duration, waited), level="info"
        )
        return view


navigator = Navigate()
navigate_to = navigator.navigate


class ViaOperatorUI(Implementation):
    """UI implementation using the normal ux"""

    navigator = navigator
    register_destination_for = navigator.register
    register_method_for = MTAImplementationContext.external_for
    navigate_to = navigate_to
    name = "ViaOperatorUI"

    def __init__(self, owner):
        super(ViaOperatorUI, self).__init__(owner)
        conf = self.application.config
        self.browser_manager = BrowserManager.from_conf(conf.get("browser", {}))

    def _reset_cache(self):
        try:
            del self.widgetastic_browser
        except AttributeError:
            pass

    def __str__(self):
        return self.name

    def create_view(self, view_class, additional_context=None):
        """Method that is used to instantiate a Widgetastic View.

        Views may define ``LOCATION`` on them, that implies a :py:meth:`force_navigate` call with
        ``LOCATION`` as parameter.

        Args:
            view_class: A view class, subclass of ``widgetastic.widget.View``
            additional_context: Additional informations passed to the view (user name, VM name, ...)
                which is also passed to the :py:meth:`force_navigate` in case when navigation is
                requested.

        Returns:
            An instance of the ``view_class``
        """
        additional_context = additional_context or {}
        view = view_class(
            self.widgetastic_browser, additional_context=additional_context, logger=logger
        )

        return view

    @cached_property
    def widgetastic_browser(self):
        """This gives us a widgetastic browser."""
        selenium_webdriver = self.browser_manager.ensure_open()
        wt = MTABrowser(selenium_webdriver, self)
        self.browser_manager.add_cleanup(self._reset_cache)
        return wt
