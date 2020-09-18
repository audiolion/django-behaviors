# -*- coding: utf-8
from django.apps import AppConfig
from django.conf import settings


class BehaviorsConfig(AppConfig):
    name = 'behaviors'

    @classmethod
    def are_slug_unique(cls):
        # By default, the Slugged behavior will generate unique slugs.
        # You can disable this constraint in your project's settings module.
        return getattr(settings, "UNIQUE_SLUG_BEHAVIOR", True)
