"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Dict, Optional, Tuple, Type
import sys
import traceback
from contextlib import contextmanager

from pkg_resources import get_distribution
import raven
import cherrypy
from cocktail.events import when
from woost import app
from woost.models import get_setting, AuthorizationError
from woost.authentication import AuthenticationFailedError
from woost.controllers.cmscontroller import CMSController


@when(CMSController.exception_raised)
def _handle_exception(e):
    try:
        sentry = get_sentry()
        if sentry:
            sentry.capture_exception(exception = e.exception)
    except Exception as error:
        sys.stderr.write("Error while sending an exception to Sentry:\n")
        traceback.print_exception(
            type(error),
            error,
            error.__traceback__,
            file=sys.stderr
        )


class Sentry:

    ignored_exception_types: Tuple[Type[Exception]] = (
        AuthorizationError,
        AuthenticationFailedError
    )

    tags: Dict[str, str] = {}

    def __init__(self, dsn: str):
        self._client = raven.Client(dsn)
        self.tags = self.tags.copy()
        self.tags.update(
            framework="woost",
            woost=get_distribution("woost").version,
            cocktail=get_distribution("cocktail").version
        )

    def get_data_from_request(self):
        """Returns request data extracted from the active request."""
        request = cherrypy.request
        return {
            'sentry.interfaces.Http': {
                'url': cherrypy.url(),
                'query_string': request.query_string,
                'method': request.method,
                'data': request.params,
                'headers': request.headers,
                'env': {
                    'SERVER_NAME': cherrypy.server.socket_host,
                    'SERVER_PORT': cherrypy.server.socket_port
                }
            }
        }

    def update_context(self, kwargs: dict):

        data = kwargs.get("data")
        if data is None:
            kwargs["data"] = self.get_data_from_request()

        tags = self.tags.copy()
        if "tags" in kwargs:
            tags.update(kwargs["tags"])

        kwargs["tags"] = tags

    def should_capture_exception(self, exception: Exception) -> bool:

        if isinstance(exception, self.ignored_exception_types):
            return False

        if (
            isinstance(exception, cherrypy.HTTPError)
            and exception.status != 500
        ):
            return False

        return True

    def capture_exception(self, exception: Exception, **kwargs):
        if self.should_capture_exception(exception):
            self.update_context(kwargs)
            return self._client.captureException(**kwargs)

    def capture_message(self, message: str, **kwargs):
        self.update_context(kwargs)
        return self._client.captureMessage(message, **kwargs)


sentry_class: Type[Sentry] = Sentry
_instances: Dict[str, Sentry] = {}


def get_sentry(dsn: str = None) -> Optional[Sentry]:

    if not dsn:
        dsn = get_setting("x_sentry_dsn")
        if not dsn:
            return None

    try:
        return _instances[dsn]
    except KeyError:
        instance = sentry_class(dsn)
        _instances[dsn] = instance
        return instance


@contextmanager
def sentry_reporting(dsn: str = None):
    sentry = get_sentry(dsn)
    try:
        yield sentry
    except Exception as exc:
        if sentry:
            sentry.capture_exception(exception=exc)

