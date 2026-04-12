from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse

from .models import UserProfile
from .forms import UserProfileForm


def register(request):
    """Cadastro de novo usuário"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Cria o perfil automaticamente
            UserProfile.objects.get_or_create(user=user)
            
            messages.success(
                request, 
                '✅ Conta criada com sucesso! Agora faça login para entrar na loja.'
            )
            
            return redirect('accounts:login')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def perfil_view(request):
    """Página de edição do perfil do usuário"""
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()   # Cloudinary faz o upload automaticamente
            messages.success(request, '✅ Perfil atualizado com sucesso! Foto salva no Cloudinary.')
            return redirect('accounts:perfil')
        else:
            messages.error(request, '❌ Erro ao salvar o perfil. Verifique os campos.')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'user': request.user,           # ← usado no template
        'profile': profile,             # ← para compatibilidade extra
    }
    return render(request, 'accounts/perfil.html', context)


# ==================== NOTIFICAÇÕES EM TEMPO REAL ====================
@login_required
def get_notifications(request):
    """Retorna notificações não lidas em formato JSON"""
    notifications = request.user.notifications.filter(is_read=False)
    
    data = {
        'unread_count': notifications.count(),
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'icon': n.icon,
                'time': n.created_at.strftime('%d/%m %H:%M')
            } for n in notifications[:5]
        ]
    }
    return JsonResponse(data)