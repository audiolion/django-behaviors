from django.views.generic.edit import CreateView, UpdateView

from .models import AuthoredMock, EditoredMock
from .forms import AuthoredMockModelForm, EditoredMockModelForm

class AuthoredMockCreateView(CreateView):
    model = Authored
    form = AuthoredMockModelForm
