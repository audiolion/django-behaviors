from django import forms

from .compat import is_authenticated


class AuthoredModelForm(forms.ModelForm):
    class Meta:
        fields = []

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(AuthoredModelForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(AuthoredModelForm, self).save(commit=False)

        if self.request is not None and is_authenticated(self.request.user):
            if not obj.pk:
                obj.author = self.request.user

        if commit:
            obj.save()
        return obj


class EditoredModelForm(forms.ModelForm):
    class Meta:
        fields = []

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(EditoredModelForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(EditoredModelForm, self).save(commit=False)

        if self.request is not None and is_authenticated(self.request.user):
            obj.editor = self.request.user

        if commit:
            obj.save()
        return obj
