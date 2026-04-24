from django import forms
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['cidade', 'texto', 'rating', 'foto']
        
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Conte sua experiência com a loja...',
                'class': 'form-control'
            }),
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'cidade': forms.TextInput(attrs={
                'placeholder': 'Ex: La Paz - BO',
                'class': 'form-control'
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
        
        labels = {
            'cidade': 'Cidade / Estado',
            'texto': 'Seu depoimento',
            'rating': 'Quantas estrelas você dá?',
            'foto': 'Foto sua (opcional)',
        }