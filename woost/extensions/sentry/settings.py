"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.translations import translations
from woost.models import add_setting

translations.load_bundle("woost.extensions.sentry.settings")

add_setting(
    schema.String(
        "x_sentry_dsn"
    )
)

