from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


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
            'nome_completo',
            'phone',
            'address',
            'sexo',
            'estado_civil',
        ]
        labels = {
            'nome_completo': 'Nome Completo',
            'phone': 'Telefone / WhatsApp',
            'address': 'Endereço Completo',
            'sexo': 'Sexo',
            'estado_civil': 'Estado Civil',
        }
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Rua, número, bairro, cidade, CEP...'
            }),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }