from django import forms


class AuthoredModelForm(forms.ModelForm):
    class Meta:
        fields = []

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(AuthoredModelForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(AuthoredModelForm, self).save(commit=False)

        if self.request is not None and self.request.user.is_authenticated():
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

        if self.request is not None and self.request.user.is_authenticated():
            obj.editor = self.request.user

        if commit:
            obj.save()
        return obj
