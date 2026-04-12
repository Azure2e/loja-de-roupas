from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from phonenumber_field.formfields import PhoneNumberField


# ==================== FORMULÁRIO DE CADASTRO (Registro) ====================
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# ==================== FORMULÁRIO DE PERFIL DO USUÁRIO ====================
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'picture',          # ← Campo de foto de perfil
            'nome_completo',
            'phone',
            'sexo',
            'estado_civil',
            'address',
        ]
        widgets = {
            'picture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome completo'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+55 11 99999-9999'
            }),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'estado_civil': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Rua, número, bairro, cidade...'
            }),
        }
        labels = {
            'picture': 'Foto de Perfil',
            'nome_completo': 'Nome Completo',
            'phone': 'Telefone / WhatsApp',
            'sexo': 'Sexo',
            'estado_civil': 'Estado Civil',
            'address': 'Endereço Completo',
        }

    # Campo de e-mail (somente leitura)
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': True
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preenche o e-mail atual do usuário
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email