from django import forms
from .models import Rating


class RatingForm(forms.ModelForm):
    """Formulario para crear/editar calificaciones"""
    
    class Meta:
        model = Rating
        fields = ['stars', 'comment']
        widgets = {
            'stars': forms.RadioSelect(choices=[(i, f'{i}★') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Comparte tu experiencia con este espacio (opcional)...'
            }),
        }
        labels = {
            'stars': '¿Cómo calificarías este espacio?',
            'comment': 'Comentario (opcional)'
        }
