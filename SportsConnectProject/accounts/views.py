from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.contrib.auth.views import LoginView as AuthLoginView
from .forms import CustomUserCreationForm

class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Verificar si el email tiene el dominio eafit.edu.co
        email = form.cleaned_data.get('email')
        if email.endswith('@eafit.edu.co'):
            form.instance.is_student = True
        response = super().form_valid(form)
        auth_login(self.request, form.instance) 
        return response

class Login(AuthLoginView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm

    def get_success_url(self):
        return reverse_lazy('home')
