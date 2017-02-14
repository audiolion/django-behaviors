from __future__ import unicode_literals

from django.db import models


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
