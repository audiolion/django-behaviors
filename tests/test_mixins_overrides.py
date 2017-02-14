#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-behaviors
------------

Tests for `django-behaviors` mixins and managers expected behaviors
for queryset and manager methods.
"""
from django.contrib.auth import get_user_model

from test_plus.test import TestCase

from .models import (OverrideObjectsManager, MixinObjectsManager,
                     OverrideObjectsQuerySet, MixinObjectsQuerySet)


class TestOverrideObjectsManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create(
            username='u1', email='u1@test.com', password='password')
        cls.author2 = User.objects.create(
            username='NotStartWithU', email='x@test.com', password='password')
        for i in range(0, 10):
            if i == 9:
                OverrideObjectsManager.objects.create(author=cls.author2)
            else:
                OverrideObjectsManager.objects.create(author=cls.author)

    def setUp(self):
        self.author.refresh_from_db()
        self.author2.refresh_from_db()

    def test_objects_authored_by_doesnt_work(self):
        with self.assertRaises(AttributeError):
            OverrideObjectsManager.objects.authored_by(self.author.username)

    def test_authors_authored_by_work(self):
        queryset = OverrideObjectsManager.authors.authored_by(self.author.username)
        self.assertEquals(queryset.count(), 9)

    def test_custom_filter_works(self):
        queryset = OverrideObjectsManager.objects.custom_filter()
        self.assertEquals(queryset.count(), 9)


class TestMixinObjectsManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.editor = User.objects.create(
            username='u1', email='u1@test.com', password='password')
        cls.editor2 = User.objects.create(
            username='NotStartWithU', email='x@test.com', password='password')
        for i in range(0, 10):
            if i == 9:
                MixinObjectsManager.objects.create(editor=cls.editor2)
            else:
                MixinObjectsManager.objects.create(editor=cls.editor)

    def setUp(self):
        self.editor.refresh_from_db()
        self.editor2.refresh_from_db()

    def test_objects_edited_by_works(self):
        queryset = MixinObjectsManager.objects.edited_by(self.editor.username)
        self.assertEquals(queryset.count(), 9)

    def test_editors_edited_by_works(self):
        queryset = MixinObjectsManager.editors.edited_by(self.editor.username)
        self.assertEquals(queryset.count(), 9)

    def test_custom_filter_works(self):
        queryset = MixinObjectsManager.objects.custom_filter()
        self.assertEquals(queryset.count(), 9)


class TestOverrideObjectsQuerySet(TestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(0, 10):
            if i % 2 == 0:
                OverrideObjectsQuerySet.objects.create(
                    publication_status=OverrideObjectsQuerySet.DRAFT)
            else:
                OverrideObjectsQuerySet.objects.create(
                    publication_status=OverrideObjectsQuerySet.PUBLISHED)

    def test_objects_draft_published_doesnt_work(self):
        with self.assertRaises(AttributeError):
            OverrideObjectsQuerySet.objects.draft()
        with self.assertRaises(AttributeError):
            OverrideObjectsQuerySet.objects.published()

    def test_publications_draft_published_by_work(self):
        queryset = OverrideObjectsQuerySet.publications.draft()
        self.assertEquals(queryset.count(), 5)
        queryset = OverrideObjectsQuerySet.publications.published()
        self.assertEquals(queryset.count(), 5)

    def test_custom_filter_works(self):
        queryset = OverrideObjectsQuerySet.objects.custom_filter()
        self.assertEquals(queryset.count(), 5)


class TestMixinObjectsQuerySet(TestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(0, 10):
            if i % 2 == 0:
                MixinObjectsQuerySet.objects.create(
                    publication_status=MixinObjectsQuerySet.DRAFT)
            else:
                MixinObjectsQuerySet.objects.create(
                    publication_status=MixinObjectsQuerySet.PUBLISHED)

    def test_objects_draft_published_works(self):
        queryset = MixinObjectsQuerySet.objects.draft()
        self.assertEquals(queryset.count(), 5)
        queryset = MixinObjectsQuerySet.objects.published()
        self.assertEquals(queryset.count(), 5)

    def test_publications_draft_published_works(self):
        queryset = MixinObjectsQuerySet.publications.draft()
        self.assertEquals(queryset.count(), 5)
        queryset = MixinObjectsQuerySet.publications.published()
        self.assertEquals(queryset.count(), 5)

    def test_custom_filter_works(self):
        queryset = MixinObjectsQuerySet.objects.custom_filter()
        self.assertEquals(queryset.count(), 5)
