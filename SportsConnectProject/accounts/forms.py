from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'last_name2', 'phone', 'password1', 'password2']
        labels = {
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Primer apellido',
            'last_name2': 'Segundo apellido',
            'phone': 'Celular',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        help_texts = {
            'password1': 'Tu contraseña debe tener al menos 8 caracteres y no debe ser completamente numérica.',
        }