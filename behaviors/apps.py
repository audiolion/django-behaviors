# -*- coding: utf-8
from django.apps import AppConfig


class BehaviorsConfig(AppConfig):
    name = 'behaviors'

    def ready(self):
        from . import signals
