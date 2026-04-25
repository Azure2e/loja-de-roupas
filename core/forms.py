from django import forms
from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['cidade', 'texto', 'rating', 'foto']

        widgets = {
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: La Paz - Bolívia ou São Paulo - SP'
            }),
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Conte sua experiência com a loja... O que você mais gostou?'
            }),
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

        labels = {
            'cidade': '🏙️ Sua cidade / Estado',
            'texto': '💭 Seu depoimento',
            'rating': '⭐ Qual sua avaliação?',
            'foto': '📸 Foto sua (opcional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Estrelas mais bonitas e descritivas
        self.fields['rating'].choices = [
            (5, '★★★★★ Excelente'),
            (4, '★★★★☆ Muito Bom'),
            (3, '★★★☆☆ Bom'),
            (2, '★★☆☆☆ Regular'),
            (1, '★☆☆☆☆ Ruim'),
        ]