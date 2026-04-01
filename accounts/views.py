from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import UserProfile


def register(request):
    """Cadastro de novo usuário"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Cria o perfil automaticamente
            UserProfile.objects.get_or_create(user=user)
            
            login(request, user)  # login automático após cadastro
            
            messages.success(request, 'Conta criada com sucesso! Bem-vindo(a) à SuaLoja!')
            return redirect('core:home')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})