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
        from behaviors.behaviors import Published
        return self.filter(publication_status=Published.DRAFT)

    def published(self):
        from behaviors.behaviors import Published
        return self.filter(publication_status=Published.PUBLISHED)
