#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-behaviors
------------

Tests for `django-behaviors` querysets module.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone

from test_plus.test import TestCase

from datetime import timedelta

from .models import AuthoredMock, EditoredMock, PublishedMock, ReleasedMock, StoreDeletedMock


class TestAuthoredQuerySet(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create(
            username='u1', email='u1@test.com', password='password')
        cls.author2 = User.objects.create(
            username='u2', email='u2@test.com', password='password')
        for i in range(0, 10):
            if i == 9:
                AuthoredMock.objects.create(author=cls.author2)
            else:
                AuthoredMock.objects.create(author=cls.author)

    def setUp(self):
        self.author.refresh_from_db()
        self.author2.refresh_from_db()

    def test_objects_all_not_affected(self):
        queryset = AuthoredMock.objects.all()
        self.assertIsNotNone(queryset)
        self.assertEqual(AuthoredMock.objects.all().count(), 10)

    def test_objects_authored_by(self):
        queryset = AuthoredMock.objects.authored_by(self.author)
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 9)
        for record in queryset:
            self.assertEqual(record.author, self.author)
        queryset = AuthoredMock.objects.authored_by(self.author2)
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 1)
        for record in queryset:
            self.assertEqual(record.author, self.author2)

    def test_objects_authored_by_no_results(self):
        queryset = AuthoredMock.objects.authored_by('Nobody')
        self.assertEqual(queryset.count(), 0)

    def test_authors_all_not_affected(self):
        queryset = AuthoredMock.authors.all()
        self.assertIsNotNone(queryset)
        self.assertEqual(AuthoredMock.authors.all().count(), 10)

    def test_authors_authored_by(self):
        queryset = AuthoredMock.authors.authored_by(self.author)
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 9)
        for record in queryset:
            self.assertEqual(record.author, self.author)
        queryset = AuthoredMock.authors.authored_by(self.author2)
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 1)
        for record in queryset:
            self.assertEqual(record.author, self.author2)

    def test_authors_authored_by_no_results(self):
        queryset = AuthoredMock.authors.authored_by('Nobody')
        self.assertEqual(queryset.count(), 0)


class TestEditoredQuerySet(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.editor = User.objects.create(
            username='u1', email='u1@test.com', password='password')
        cls.editor2 = User.objects.create(
            username='u2', email='u2@test.com', password='password')
        for i in range(0, 10):
            if i == 0:
                EditoredMock.objects.create()
            elif i == 9:
                EditoredMock.objects.create(editor=cls.editor2)
            else:
                EditoredMock.objects.create(editor=cls.editor)

    def setUp(self):
        self.editor.refresh_from_db()
        self.editor2.refresh_from_db()

    def test_empty_editor_returns_all(self):
        queryset = EditoredMock.objects.edited_by('')
        self.assertEqual(queryset.count(), 9)

    def test_objects_all_not_affected(self):
        queryset = EditoredMock.objects.all()
        self.assertIsNotNone(queryset)
        self.assertEqual(EditoredMock.objects.all().count(), 10)

    def test_objects_editored_by(self):
        queryset = EditoredMock.objects.edited_by(self.editor)
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 8)
        for record in queryset:
            self.assertEqual(record.editor, self.editor)
        queryset = EditoredMock.objects.edited_by(self.editor2)
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 1)
        for record in queryset:
            self.assertEqual(record.editor, self.editor2)

    def test_editors_editored_by_no_results(self):
        queryset = EditoredMock.editors.edited_by('Nobody')
        self.assertEqual(queryset.count(), 0)

    def test_editors_editored_by(self):
        queryset = EditoredMock.editors.edited_by(self.editor)
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 8)
        for record in queryset:
            self.assertEqual(record.editor, self.editor)
        queryset = EditoredMock.editors.edited_by(self.editor2)
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 1)
        for record in queryset:
            self.assertEqual(record.editor, self.editor2)


class TestPublishedQuerySet(TestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(0, 10):
            if i % 2 == 0:
                PublishedMock.objects.create()
            else:
                PublishedMock.objects.create(publication_status=PublishedMock.PUBLISHED)

    def test_objects_all_not_affected(self):
        queryset = PublishedMock.objects.all()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 10)

    def test_manager_draft(self):
        queryset = PublishedMock.objects.draft()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 5)
        for record in queryset:
            self.assertEqual(record.publication_status, PublishedMock.DRAFT)

    def test_manager_published(self):
        queryset = PublishedMock.objects.published()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 5)
        for record in queryset:
            self.assertEqual(
                record.publication_status, PublishedMock.PUBLISHED)


class TestReleasedQuerySet(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.past_date = timezone.now() - timedelta(weeks=1)
        cls.future_date = timezone.now() + timedelta(weeks=1)
        for i in range(0, 10):
            if i % 2 == 0:
                ReleasedMock.objects.create(release_date=cls.past_date)
            elif i == 1:
                ReleasedMock.objects.create()
            else:
                ReleasedMock.objects.create(release_date=cls.future_date)

    def test_objects_all_not_affected(self):
        queryset = ReleasedMock.objects.all()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 10)

    def test_manager_released(self):
        queryset = ReleasedMock.objects.released()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 5)
        for record in queryset:
            self.assertEqual(record.release_date, self.past_date)

    def test_manager_not_released(self):
        queryset = ReleasedMock.objects.not_released()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 4)
        for record in queryset:
            self.assertEqual(record.release_date, self.future_date)

    def test_manager_no_release_date(self):
        queryset = ReleasedMock.objects.no_release_date()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 1)
        for record in queryset:
            self.assertIsNone(record.release_date)


class TestStoreDeletedQuerySet(TestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(0, 10):
            if i % 2 == 0:
                StoreDeletedMock.objects.create()
            else:
                StoreDeletedMock.objects.create().delete()

    def test_object_all_returns_only_not_deleted_models(self):
        queryset = StoreDeletedMock.objects.all()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 5)
        for record in queryset:
            self.assertIsNone(record.deleted)

    def test_deleted_returns_only_deleted_models(self):
        queryset = StoreDeletedMock.objects.deleted()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 5)
        for record in queryset:
            self.assertIsNotNone(record.deleted)
            self.assertEqual(record.deleted.date(), timezone.now().date())

    def test_not_deleted_returns_only_not_deleted_models(self):
        queryset = StoreDeletedMock.objects.not_deleted()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 5)
        for record in queryset:
            self.assertIsNone(record.deleted)

    def test_allow_deleted_returns_all_models(self):
        queryset = StoreDeletedMock.objects.allow_deleted()
        self.assertIsNotNone(queryset)
        self.assertEqual(queryset.count(), 10)
