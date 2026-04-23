from django import forms
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['cidade', 'texto', 'rating', 'foto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Conte sua experiência...'}),
            'rating': forms.RadioSelect(),
        }
        labels = {
            'cidade': 'Sua cidade/estado',
            'texto': 'Seu depoimento',
            'rating': 'Quantas estrelas?',
            'foto': 'Foto (opcional)',
        }