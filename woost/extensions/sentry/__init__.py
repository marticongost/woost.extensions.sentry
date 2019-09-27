"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Optional, Type
from . import settings, admin
from .installation import install
from .sentry import get_sentry, Sentry, sentry_reporting, ignored_by_sentry

