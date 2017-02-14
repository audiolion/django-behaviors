from behaviors.forms import AuthoredModelForm, EditoredModelForm

from .models import AuthoredMock, EditoredMock


class AuthoredModelFormMock(AuthoredModelForm):
    class Meta:
        model = AuthoredMock
        fields = []


class EditoredModelFormMock(EditoredModelForm):
    class Meta:
        model = EditoredMock
        fields = []
