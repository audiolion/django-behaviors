from django.db import models

from behaviors.behaviors import Authored, Editored, Published, Timestamped
from behaviors.managers import (AuthoredManager, EditoredManager,
                                PublishedManager)
from behaviors.querysets import PublishedQuerySet


class AuthoredMock(Authored):
    pass


class EditoredMock(Editored):
    pass


class PublishedMock(Published):
    pass


class TimestampedMock(Timestamped):
    pass


class AuthoredMockManager(Authored):
    objects = AuthoredManager()


class EditoredMockManager(Editored):
    objects = EditoredManager()


class PublishedMockManager(Published):
    objects = PublishedManager()


class OverrideManager(models.Manager):

    def get_queryset(self):
        return super(OverrideManager, self).get_queryset()

    def custom_filter(self):
        return self.get_queryset().filter(author__username__istartswith='u')


class OverrideObjectsManager(Authored):
    objects = OverrideManager()


class MixinManager(EditoredManager, models.Manager):

    def get_queryset(self):
        return super(MixinManager, self).get_queryset()

    def custom_filter(self):
        return self.get_queryset().filter(editor__username__istartswith='u')


class MixinObjectsManager(Editored):
    objects = MixinManager()


class OverrideQuerySet(models.QuerySet):

    def custom_filter(self):
        return self.filter(publication_status=Published.DRAFT)


class OverrideObjectsQuerySet(Published):
    objects = OverrideQuerySet.as_manager()


class MixinQuerySet(PublishedQuerySet, models.QuerySet):

    def custom_filter(self):
        return self.filter(publication_status=Published.DRAFT)


class MixinObjectsQuerySet(Published):
    objects = MixinQuerySet.as_manager()
