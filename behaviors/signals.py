# -*- coding: utf-8
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from .behaviors import Timestamped


@receiver(post_save)
def timestamped_modified(sender, update_fields, created, instance, **kwargs):
    if isinstance(instance, Timestamped):
        if instance.pk:
            instance.modified = timezone.now()
