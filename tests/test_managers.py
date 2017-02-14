#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-behaviors
------------

Tests for `django-behaviors` managers module.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone

from test_plus.test import TestCase

from datetime import timedelta

from behaviors.querysets import (AuthoredQuerySet, EditoredQuerySet,
                                 PublishedQuerySet, ReleasedQuerySet)

from .models import (AuthoredMockManager, EditoredMockManager,
                     PublishedMockManager, ReleasedMockManager)


class TestAuthoredMockManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create(
            username='u1', email='u1@test.com', password='password')
        cls.author2 = User.objects.create(
            username='u2', email='u2@test.com', password='password')
        for i in range(0, 10):
            if i == 9:
                AuthoredMockManager.objects.create(author=cls.author2)
            else:
                AuthoredMockManager.objects.create(author=cls.author)

    def setUp(self):
        self.author.refresh_from_db()
        self.author2.refresh_from_db()

    def test_manager_get_queryset_returns_authored_queryset(self):
        queryset = AuthoredMockManager.objects.get_queryset()
        self.assertTrue(type(queryset) is AuthoredQuerySet)

    def test_authored_by_manager_method(self):
        queryset = AuthoredMockManager.objects.authored_by('u')
        self.assertEquals(queryset.count(), 10)


class TestEditoredMockManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.editor = User.objects.create(
            username='u1', email='u1@test.com', password='password')
        cls.editor2 = User.objects.create(
            username='u2', email='u2@test.com', password='password')
        for i in range(0, 10):
            if i == 9:
                EditoredMockManager.objects.create(editor=cls.editor2)
            else:
                EditoredMockManager.objects.create(editor=cls.editor)

    def setUp(self):
        self.editor.refresh_from_db()
        self.editor2.refresh_from_db()

    def test_manager_get_queryset_returns_edited_queryset(self):
        queryset = EditoredMockManager.objects.get_queryset()
        self.assertTrue(type(queryset) is EditoredQuerySet)

    def test_edited_by_manager_method(self):
        queryset = EditoredMockManager.objects.edited_by('u')
        self.assertEquals(queryset.count(), 10)


class TestPublishedMockManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(0, 10):
            if i % 2 == 0:
                PublishedMockManager.objects.create()
            else:
                PublishedMockManager.objects.create(
                    publication_status=PublishedMockManager.PUBLISHED)

    def test_manager_get_queryset_returns_published_queryset(self):
        queryset = PublishedMockManager.objects.get_queryset()
        self.assertTrue(type(queryset) is PublishedQuerySet)

    def test_draft_manager_method(self):
        queryset = PublishedMockManager.objects.draft()
        self.assertEquals(queryset.count(), 5)

    def test_published_manager_method(self):
        queryset = PublishedMockManager.objects.published()
        self.assertEquals(queryset.count(), 5)


class TestReleasedMockManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.past_date = timezone.now() - timedelta(weeks=1)
        cls.future_date = timezone.now() + timedelta(weeks=1)
        for i in range(0, 10):
            if i % 2 == 0:
                ReleasedMockManager.objects.create(release_date=cls.past_date)
            elif i == 1:
                ReleasedMockManager.objects.create()
            else:
                ReleasedMockManager.objects.create(release_date=cls.future_date)

    def test_manager_get_queryset_returns_released_queryset(self):
        queryset = ReleasedMockManager.objects.get_queryset()
        self.assertTrue(type(queryset) is ReleasedQuerySet)

    def test_released_manager_method(self):
        queryset = ReleasedMockManager.objects.released()
        self.assertEquals(queryset.count(), 5)

    def test_not_released_manager_method(self):
        queryset = ReleasedMockManager.objects.not_released()
        self.assertEquals(queryset.count(), 4)

    def test_no_release_date_manager_method(self):
        queryset = ReleasedMockManager.objects.no_release_date()
        self.assertEquals(queryset.count(), 1)
