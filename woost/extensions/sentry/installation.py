"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import ExtensionAssets


def install():
    """Creates the assets required by the sentry extension."""

    assets = ExtensionAssets("sentry")

