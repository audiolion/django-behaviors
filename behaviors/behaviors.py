from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

try:
    from slugify import slugify
except ImportError:
    from django.utils.text import slugify

from .apps import BehaviorsConfig
from .querysets import (AuthoredQuerySet, EditoredQuerySet,
                        PublishedQuerySet, ReleasedQuerySet,
                        StoreDeletedQuerySet)


class Authored(models.Model):
    """
    An abstract behavior representing adding an author to a model based on the
    AUTH_USER_MODEL setting.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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
        on_delete=models.SET_NULL,
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


class Released(models.Model):
    """
    An abstract behavior representing a release_date for a model to
    indicate when it should be listed publically.
    """
    release_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    objects = ReleasedQuerySet.as_manager()
    releases = ReleasedQuerySet.as_manager()

    def release_on(self, date=None):
        if not date:
            date = timezone.now()
        self.release_date = date
        self.save()

    @property
    def released(self):
        return self.release_date and self.release_date < timezone.now()


class Slugged(models.Model):
    """
    An abstract behavior representing adding a slug (by default, unique) to
    a model based on the slug_source property.
    """
    slug = models.SlugField(
        max_length=255,
        unique=BehaviorsConfig.are_slug_unique(),
        blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug() \
                if BehaviorsConfig.are_slug_unique() else self.get_slug()
        super(Slugged, self).save(*args, **kwargs)

    def get_slug(self):
        try:
            return slugify(getattr(self, "slug_source"), to_lower=True)
        except TypeError:
            # django.utils.text.slugify fallback
            return slugify(getattr(self, "slug_source"))

    def is_unique_slug(self, slug):
        qs = self.__class__.objects.filter(slug=slug)
        return not qs.exists()

    def generate_unique_slug(self):
        slug = self.get_slug()
        new_slug = slug

        iteration = 1
        while not self.is_unique_slug(new_slug):
            new_slug = "%s-%d" % (slug, iteration)
            iteration += 1

        return new_slug


class Timestamped(models.Model):
    """
    An abstract behavior representing timestamping a model with``created`` and
    ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    @property
    def changed(self):
        return True if self.modified else False

    def save(self, *args, **kwargs):
        if self.pk:
            self.modified = timezone.now()
        return super(Timestamped, self).save(*args, **kwargs)


class StoreDeleted(models.Model):
    """
    An abstract behavior representing store deleted a model with``deleted`` field,
    avoiding the model object to be deleted and allowing you to restore it.
    """
    deleted = models.DateTimeField(null=True, blank=True)

    objects = StoreDeletedQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted is not None

    def delete(self, *args, **kwargs):
        if not self.pk:
            raise ObjectDoesNotExist(
                'Object must be created before it can be deleted')
        self.deleted = timezone.now()
        return super(StoreDeleted, self).save(*args, **kwargs)

    def restore(self, *args, **kwargs):
        if not self.pk:
            raise ObjectDoesNotExist(
                'Object must be created before it can be restored')
        self.deleted = None
        return super(StoreDeleted, self).save(*args, **kwargs)
