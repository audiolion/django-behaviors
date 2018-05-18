from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class AuthoredQuerySet(models.QuerySet):

    def authored_by(self, author):
        return self.filter(author__username__istartswith=author)


class EditoredQuerySet(models.QuerySet):

    def edited_by(self, editor):
        return self.filter(editor__username__istartswith=editor)


class PublishedQuerySet(models.QuerySet):

    def draft(self):
        return self.filter(publication_status='d')

    def published(self):
        return self.filter(publication_status='p')


class ReleasedQuerySet(models.QuerySet):

    def released(self):
        return self.filter(~models.Q(release_date=None)).filter(
            release_date__lte=timezone.now())

    def not_released(self):
        return self.filter(~models.Q(release_date=None)).filter(
            release_date__gt=timezone.now())

    def no_release_date(self):
        return self.filter(models.Q(release_date=None))


class StoreDeletedQuerySet(models.QuerySet):

    def get_queryset(self):
        return self.not_deleted()

    def deleted(self):
        return self.exclude(deleted__isnull=True)

    def not_deleted(self):
        return self.exclude(deleted__isnull=False)

    def allow_deleted(self):
        return self
