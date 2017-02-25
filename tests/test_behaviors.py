#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-behaviors
------------

Tests for `django-behaviors` behaviors module.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone

from test_plus.test import TestCase

from datetime import timedelta

from .models import (AuthoredMock, EditoredMock, PublishedMock,
                     ReleasedMock, SluggedMock, TimestampedMock)


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
        self.assertTrue(self.mock.slug, "slugged-title")

    def test_generate_unique_slug(self):
        self.assertTrue(self.mock.slug, "slugged-title")
        self.assertTrue(self.mock2.slug, "slugged-title-1")
        self.assertTrue(self.mock3.slug, "slugged-title-2")


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
