from django.contrib import admin
from django.contrib.auth.views import login
from django.urls import include, path
from . import views
from django.views.generic import TemplateView

app_name = 'usuario'

urlpatterns = [
    path('login/', login, {'template_name':'usuario/login.html'}, name='login'),
    path('registrar/', views.registrar, name='registrar'),
]