#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-behaviors
------------

Tests for `django-behaviors` behaviors module.
"""
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from test_plus.test import TestCase

from datetime import timedelta

from .models import (AuthoredMock, EditoredMock, PublishedMock,
                     ReleasedMock, SluggedMock, NonUniqueSluggedMock,
                     TimestampedMock, StoreDeletedMock)


class TestAuthored(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create(
            username='u1', email='u1@example.com', password='password')
        cls.mock = AuthoredMock.objects.create(author=cls.author)

    def setUp(self):
        self.author.refresh_from_db()
        self.mock.refresh_from_db()

    def test_author_field_label(self):
        field_label = self.mock._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'author')

    def test_author_exists(self):
        self.assertIsNotNone(self.mock.author)
        self.assertEqual(self.mock.author, self.author)

    def test_author_related_name(self):
        related_name = self.mock._meta.get_field('author').related_query_name()
        self.assertEqual(related_name, 'tests_authoredmock_author')


class TestEditored(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.editor = User.objects.create(
            username='u1', email='u1@example.com', password='password')
        cls.mock = EditoredMock.objects.create()

    def setUp(self):
        self.editor.refresh_from_db()
        self.mock.refresh_from_db()

    def test_editor_field_label(self):
        field_label = self.mock._meta.get_field('editor').verbose_name
        self.assertEqual(field_label, 'editor')

    def test_editor_doesnt_exist(self):
        self.assertIsNone(self.mock.editor)

    def test_editor_exists(self):
        self.mock.editor = self.editor
        self.mock.save()
        self.assertIsNotNone(self.mock.editor)
        self.assertEqual(self.mock.editor, self.editor)

    def test_editor_related_name(self):
        related_name = self.mock._meta.get_field('editor').related_query_name()
        self.assertEqual(related_name, 'tests_editoredmock_editor')


class TestPublished(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.mock = PublishedMock.objects.create()

    def setUp(self):
        self.mock.refresh_from_db()

    def test_draft_true_by_default(self):
        self.assertTrue(self.mock.draft)

    def test_published_property(self):
        self.mock.publication_status = PublishedMock.PUBLISHED
        self.mock.save()
        self.assertTrue(self.mock.published)


class TestReleased(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.mock = ReleasedMock.objects.create()
        cls.mock2 = ReleasedMock.objects.create(release_date=timezone.now())

    def setUp(self):
        self.mock.refresh_from_db()
        self.mock2.refresh_from_db()

    def test_nullable_release_date(self):
        self.assertIsNone(self.mock.release_date)

    def test_nulled_release_date_released_is_false(self):
        self.assertFalse(self.mock.released)

    def test_future_release_date_released_is_false(self):
        week_in_advance = timezone.now() + timedelta(weeks=1)
        self.mock.release_date = week_in_advance
        self.mock.save()
        self.assertFalse(self.mock.released)

    def test_past_release_date_released_is_true(self):
        self.mock.release_date = timezone.now()
        self.mock.save()
        self.assertTrue(self.mock.released)

    def test_release_on_no_date_provided(self):
        self.mock.release_on()
        self.assertTrue(self.mock.released)

    def test_release_on_future_date_provided(self):
        week_in_advance = timezone.now() + timedelta(weeks=1)
        self.mock.release_on(week_in_advance)
        self.assertFalse(self.mock.released)

    def test_release_on_past_date_provided(self):
        self.mock.release_on(timezone.now())
        self.assertTrue(self.mock.released)


class TestSlugged(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.mock = SluggedMock.objects.create(title="Slugged Title")
        cls.mock2 = SluggedMock.objects.create(title="Slugged TITLE")
        cls.mock3 = SluggedMock.objects.create(title="SLUGGED Title")

    def setUp(self):
        self.mock.refresh_from_db()
        self.mock2.refresh_from_db()
        self.mock3.refresh_from_db()

    def test_title_field_slugged(self):
        self.assertEqual(self.mock.slug, "slugged-title")

    def test_generate_unique_slug(self):
        self.assertEqual(self.mock.slug, "slugged-title")
        self.assertEqual(self.mock2.slug, "slugged-title-1")
        self.assertEqual(self.mock3.slug, "slugged-title-2")


@override_settings(UNIQUE_SLUG_BEHAVIOR=False)
class TestNonUniqueSlugged(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.mock = NonUniqueSluggedMock.objects.create(title="Slugged Title")
        cls.mock2 = NonUniqueSluggedMock.objects.create(title="Slugged TITLE")
        cls.mock3 = NonUniqueSluggedMock.objects.create(title="SLUGGED Title")

    def setUp(self):
        self.mock.refresh_from_db()
        self.mock2.refresh_from_db()
        self.mock3.refresh_from_db()

    def test_generate_non_unique_slug(self):
        self.assertEqual(self.mock.slug, "slugged-title")
        self.assertEqual(self.mock2.slug, "slugged-title")
        self.assertEqual(self.mock3.slug, "slugged-title")


class TestTimestamped(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.mock = TimestampedMock.objects.create()

    def setUp(self):
        self.mock.refresh_from_db()

    def test_timestamp_changed_initially_false(self):
        self.assertFalse(self.mock.changed)

    def test_timestamp_changed_after_save(self):
        self.mock.save()
        self.assertTrue(self.mock.changed)


class TestStoreDeleted(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.mock_to_delete = StoreDeletedMock.objects.create()
        cls.mock_to_restore = StoreDeletedMock.objects.create()

    def setUp(self):
        self.mock_to_delete.refresh_from_db()

    def test_delete_model(self):
        self.mock_to_delete.delete()
        self.assertIsNotNone(self.mock_to_delete.deleted)

    def test_restore_model(self):
        self.mock_to_restore.delete()
        self.mock_to_restore.restore()
        self.assertIsNone(self.mock_to_restore.deleted)

    def test_delete_not_created_object_raises_exception(self):
        mock = StoreDeletedMock()
        self.assertIsNone(mock.pk)
        with self.assertRaises(ObjectDoesNotExist) as raises_context:
            mock.delete()
            self.assertIsNotNone(raises_context)

    def test_restore_not_created_object_raises_exception(self):
        mock = StoreDeletedMock()
        self.assertIsNone(mock.pk)
        with self.assertRaises(ObjectDoesNotExist) as raises_context:
            mock.restore()
            self.assertIsNotNone(raises_context)

    def test_is_deleted_property_returns_true_when_delete_object(self):
        self.mock_to_delete.delete()
        self.assertTrue(self.mock_to_delete.is_deleted)

    def test_is_deleted_property_returns_false_when_restore_object(self):
        self.mock_to_restore.delete()
        self.mock_to_restore.restore()
        self.assertFalse(self.mock_to_restore.is_deleted)

    def test_is_deleted_property_returns_false_when_create_object(self):
        mock = StoreDeletedMock()
        mock.save()
        self.assertFalse(mock.is_deleted)
