from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django import forms
from django.core.exceptions import ValidationError


class RegistroForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]
        labels = {

            'username':'Usuario',
            'first_name':'Nombre',
            'last_name':'Apellidos',
            'email':'Email',


        }
        '''
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control',
                                               'placeholder':'Usuario'}),

            'first_name': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Nombre'}),

            'last_name': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Apellidos'}),

            'email': forms.EmailInput(attrs={'class': 'form-control',
                                               'placeholder': 'Email'}),

            'password1': forms.PasswordInputattrs={'class': 'form-control',
                                             'placeholder': 'Contraseña'},
        }
        '''



class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='', min_length=4, max_length=150, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Usuario'}))
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirma contraseña'}))

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("Usuario ya existe")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email ya existe")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user