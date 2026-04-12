from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse

from .models import UserProfile
from .forms import UserProfileForm


def register(request):
    """Cadastro de novo usuário"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, '✅ Conta criada com sucesso! Agora faça login.')
            return redirect('accounts:login')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def perfil(request):
    """Página de edição do perfil do usuário (Cloudinary)"""
    profile = request.user.profile

    if request.method == 'POST':
        # ==================== REMOVER FOTO ====================
        if 'remove_picture' in request.POST:
            if profile.picture:
                profile.picture.delete()           # deleta do Cloudinary
                profile.picture = None
                profile.save()
                messages.success(request, '🗑️ Foto removida com sucesso!')
                return redirect('accounts:perfil')

        # ==================== ATUALIZAR PERFIL ====================
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            saved_profile = form.save()
            
            if saved_profile.picture and request.FILES.get('picture'):
                print("✅ FOTO SALVA NO CLOUDINARY:", saved_profile.picture.url)
                messages.success(request, '✅ Perfil atualizado! Foto salva com sucesso.')
            else:
                messages.success(request, '✅ Perfil atualizado com sucesso!')
            
            return redirect('accounts:perfil')
        else:
            messages.error(request, '❌ Erro ao salvar o perfil. Verifique os campos.')

    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'accounts/perfil.html', context)


# ==================== NOTIFICAÇÕES ====================
@login_required
def get_notifications(request):
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