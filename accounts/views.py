import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse

from .models import UserProfile
from .forms import UserProfileForm

logger = logging.getLogger(__name__)  # ← adicione isso no topo


def register(request):
    """Cadastro de novo usuário"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Cria o perfil automaticamente (mesmo que já exista)
            UserProfile.objects.get_or_create(user=user)
            messages.success(
                request,
                '✅ Conta criada com sucesso! Agora faça login.'
            )
            return redirect('accounts:login')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def perfil(request):
    """Página de edição do perfil do usuário (Cloudinary)"""
    # Segurança extra: garante que o perfil sempre existe
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            try:
                saved_profile = form.save()

                if saved_profile.picture:
                    logger.info(f"✅ Foto salva no Cloudinary: {saved_profile.picture.url}")
                    messages.success(request, '✅ Perfil atualizado com sucesso! Foto salva.')
                else:
                    logger.warning("⚠️ Perfil salvo, mas campo 'picture' veio vazio do Cloudinary")
                    messages.warning(request, '⚠️ Perfil atualizado, mas a foto não foi enviada.')

                return redirect('accounts:perfil')

            except Exception as e:
                logger.error(f"❌ Erro no upload Cloudinary: {e}", exc_info=True)
                messages.error(request, f'❌ Erro ao salvar foto: {e}')
        else:
            # Mostra os erros do formulário (muito útil!)
            logger.warning(f"❌ Erros no formulário de perfil: {form.errors}")
            messages.error(request, '❌ Erro ao salvar o perfil. Verifique os campos.')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'user': request.user,
        'profile': profile,
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