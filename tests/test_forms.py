#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-behaviors
------------

Tests for `django-behaviors` forms module.
"""
from django.contrib.auth import get_user_model

from django.test import TransactionTestCase
from django.test.client import RequestFactory


from .forms import AuthoredModelFormMock, EditoredModelFormMock
from .models import AuthoredMock, EditoredMock


class TestAuthoredModelForm(TransactionTestCase):

    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create(
            username='u1', email='u1@test.com', password='password')
        self.requests = RequestFactory()

    def test_author_added_to_form_on_save(self):
        self.assertEqual(AuthoredMock.objects.all().count(), 0)
        request = self.requests.get('/')
        request.user = self.author
        form = AuthoredModelFormMock(data={}, request=request)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(AuthoredMock.objects.all().count(), 1)
        obj = AuthoredMock.objects.get(id=1)
        self.assertIsNotNone(obj.author)
        self.assertEqual(obj.author, self.author)

    def test_integrity_error_when_no_author_and_no_request_provided(self):
        from django.db.utils import IntegrityError
        self.assertEqual(AuthoredMock.objects.all().count(), 0)
        form = AuthoredModelFormMock(data={}, request=None)
        self.assertTrue(form.is_valid())
        with self.assertRaises(IntegrityError):
            form.save()

    def test_form_updates_without_request_passed(self):
        request = self.requests.get('/')
        request.user = self.author
        form = AuthoredModelFormMock(data={}, request=request)
        form.save()
        obj = AuthoredMock.objects.all()[0]
        form = AuthoredModelFormMock(instance=obj, data={})
        form.save()
        obj.refresh_from_db()
        self.assertIsNotNone(obj.author)
        self.assertEqual(obj.author, self.author)

    def test_save_form_second_time_doesnt_change_author(self):
        User = get_user_model()
        not_author = User.objects.create(
            username='u2', email='u2@test.com', password='password')
        request = self.requests.get('/')
        request.user = self.author
        form = AuthoredModelFormMock(data={}, request=request)
        form.save()
        obj = AuthoredMock.objects.all()[0]
        request.user = not_author
        form = AuthoredModelFormMock(instance=obj, data={}, request=request)
        form.save()
        obj.refresh_from_db()
        self.assertEqual(obj.author, self.author)

    def test_commit_false_doesnt_save_and_assigns_author(self):
        request = self.requests.get('/')
        request.user = self.author
        form = AuthoredModelFormMock(data={}, request=request)
        if form.is_valid():
            obj = form.save(commit=False)
            self.assertEqual(obj.author, self.author)
            self.assertEqual(AuthoredMock.objects.all().count(), 0)


class TestEditoredModelForm(TransactionTestCase):

    def setUp(self):
        User = get_user_model()
        self.editor = User.objects.create(
            username='u1', email='u1@test.com', password='password')
        self.requests = RequestFactory()

    def test_editor_added_to_form_on_save(self):
        self.assertEqual(EditoredMock.objects.all().count(), 0)
        request = self.requests.get('/')
        request.user = self.editor
        form = EditoredModelFormMock(data={}, request=request)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(EditoredMock.objects.all().count(), 1)
        obj = EditoredMock.objects.get(id=1)
        self.assertIsNotNone(obj.editor)
        self.assertEqual(obj.editor, self.editor)

    def test_no_integrity_error_when_no_editor_provided(self):
        self.assertEqual(EditoredMock.objects.all().count(), 0)
        form = EditoredModelFormMock(data={}, request=None)
        self.assertTrue(form.is_valid())
        form.save()
        obj = EditoredMock.objects.all()[0]
        self.assertIsNone(obj.editor)

    def test_form_updates_without_request_passed(self):
        request = self.requests.get('/')
        request.user = self.editor
        form = EditoredModelFormMock(data={}, request=request)
        form.save()
        obj = EditoredMock.objects.all()[0]
        form = EditoredModelFormMock(instance=obj, data={})
        form.save()
        obj.refresh_from_db()
        self.assertIsNotNone(obj.editor)
        self.assertEqual(obj.editor, self.editor)

    def test_save_form_second_time_changes_editor(self):
        User = get_user_model()
        new_editor = User.objects.create(
            username='u2', email='u2@test.com', password='password')
        request = self.requests.get('/')
        request.user = self.editor
        form = EditoredModelFormMock(data={}, request=request)
        form.save()
        obj = EditoredMock.objects.all()[0]
        request.user = new_editor
        form = EditoredModelFormMock(instance=obj, data={}, request=request)
        form.save()
        obj.refresh_from_db()
        self.assertEqual(obj.editor, new_editor)

    def test_commit_false_doesnt_save_and_assigns_editor(self):
        request = self.requests.get('/')
        request.user = self.editor
        form = EditoredModelFormMock(data={}, request=request)
        if form.is_valid():
            obj = form.save(commit=False)
            self.assertEqual(obj.editor, self.editor)
            self.assertEqual(EditoredMock.objects.all().count(), 0)
