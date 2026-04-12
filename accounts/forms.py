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
            'picture',
            'nome_completo',
            'phone',
            'address',
            'sexo',
            'estado_civil'
        ]
        widgets = {
            'picture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'estado_civil': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'picture': 'Foto de Perfil',
            'nome_completo': 'Nome Completo',
            'phone': 'Telefone / WhatsApp',
            'address': 'Endereço Completo',
            'sexo': 'Sexo',
            'estado_civil': 'Estado Civil',
        }