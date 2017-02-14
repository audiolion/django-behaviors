from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone

from .querysets import (AuthoredQuerySet, EditoredQuerySet,
                        PublishedQuerySet)


class Authored(models.Model):
    """
    An abstract behavior representing adding an author to a model based on the
    AUTH_USER_MODEL setting.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s_author")

    objects = AuthoredQuerySet.as_manager()
    authors = AuthoredQuerySet.as_manager()

    class Meta:
        abstract = True


class Editored(models.Model):
    """
    An abstract behavior representing adding an editor to a model based on the
    AUTH_USER_MODEL setting.
    """
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s_editor",
        blank=True, null=True)

    objects = EditoredQuerySet.as_manager()
    editors = EditoredQuerySet.as_manager()

    class Meta:
        abstract = True


class Published(models.Model):
    """
    An abstract behavior representing adding a publication status. A
    ``publication_status`` is set on the model with Draft or Published
    options.
    """
    DRAFT = 'd'
    PUBLISHED = 'p'

    PUBLICATION_STATUS_CHOICES = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    )

    publication_status = models.CharField(
        "Publication Status", max_length=1,
        choices=PUBLICATION_STATUS_CHOICES, default=DRAFT)

    class Meta:
        abstract = True

    objects = PublishedQuerySet.as_manager()
    publications = PublishedQuerySet.as_manager()

    @property
    def draft(self):
        return self.publication_status == self.DRAFT

    @property
    def published(self):
        return self.publication_status == self.PUBLISHED


class Timestamped(models.Model):
    """
    An abstract behavior representing timestamping a model with``created`` and
    ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def changed(self):
        return True if self.modified else False

    def save(self, *args, **kwargs):
        if self.pk:
            self.modified = timezone.now()
        return super(Timestamped, self).save(*args, **kwargs)
