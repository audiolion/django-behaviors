from __future__ import unicode_literals

from django.db import models

from .querysets import (AuthoredQuerySet, EditoredQuerySet,
                        PublishedQuerySet, ReleasedQuerySet)


class AuthoredManager(models.Manager):

    def get_queryset(self):
        return AuthoredQuerySet(self.model, using=self._db)

    def authored_by(self, author):
        return self.get_queryset().authored_by(author)


class EditoredManager(models.Manager):

    def get_queryset(self):
        return EditoredQuerySet(self.model, using=self._db)

    def edited_by(self, editor):
        return self.get_queryset().edited_by(editor)


class PublishedManager(models.Manager):

    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self._db)

    def draft(self):
        return self.get_queryset().draft()

    def published(self):
        return self.get_queryset().published()


class ReleasedManager(models.Manager):

    def get_queryset(self):
        return ReleasedQuerySet(self.model, using=self._db)

    def released(self):
        return self.get_queryset().released()

    def not_released(self):
        return self.get_queryset().not_released()

    def no_release_date(self):
        return self.get_queryset().no_release_date()
