from django.views.generic.edit import CreateView, UpdateView

from .models import AuthoredMock, EditoredMock
from .forms import AuthoredMockModelForm, EditoredMockModelForm


class FormKwargsRequestMixin(object):

    def get_form_kwargs(self):
        kwargs = super(EditoredMockUpdateView, self).get_form_kwargs(self)
        kwargs['request'] = self.request
        return kwargs


class AuthoredMockCreateView(FormKwargsRequestMixin, CreateView):
    model = AuthoredMock
    form = AuthoredMockModelForm


class EditoredMockUpdateView(FormKwargsRequestMixin, UpdateView):
    model = EditoredMock
    form = EditoredMockModelForm
