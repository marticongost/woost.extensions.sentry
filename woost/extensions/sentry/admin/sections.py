"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.translations import translations
from woost.admin.sections import Settings
from woost.admin.sections.contentsection import ContentSection

translations.load_bundle("woost.extensions.sentry.admin.sections")


class SentrySettings(Settings):
    icon_uri = (
        "woost.extensions.sentry.admin.ui://"
        "images/sections/sentry.svg"
    )
    members = [
        "x_sentry_dsn"
    ]


@when(ContentSection.declared)
def fill(e):
    e.source.append(SentrySettings("sentry"))

