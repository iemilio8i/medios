from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.urls import reverse_lazy, reverse

from django.views.generic import CreateView

from usuario.forms import RegistroForm, CustomUserCreationForm
from django.contrib import messages


class RegistroUsuario(CreateView):
    model = User
    template_name = "usuario/registrar.html"
    form_class = RegistroForm
    success_url = reverse_lazy("medios:index")


def registrar(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Cuenta creada')
            return HttpResponseRedirect(reverse('usuario:login'))

    else:
        f = CustomUserCreationForm()

    return render(request, 'usuario/registrar.html', {'form': f})