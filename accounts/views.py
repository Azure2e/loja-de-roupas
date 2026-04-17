import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.http import JsonResponse

from django.contrib.auth.models import User

from .models import UserProfile, ChatMessage
from .forms import UserProfileForm

logger = logging.getLogger(__name__)


# ====================== FORMULÁRIO CUSTOMIZADO ======================
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# ====================== VIEWS ======================
def register(request):
    """Cadastro de novo usuário com E-MAIL (obrigatório para pagamento)"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)

            messages.success(
                request,
                '✅ Conta criada com sucesso! Agora faça login.'
            )
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def perfil(request):
    """Página de edição do perfil do usuário (Cloudinary)"""
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


# ==================== CHECKOUT ====================
@login_required
def checkout(request):
    """Página de Checkout Seguro com resumo do carrinho"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    carrinho = request.session.get('carrinho', {})

    subtotal_geral = 0
    for item in carrinho.values():
        subtotal_geral += float(item.get('subtotal', 0))

    desconto = float(request.session.get('desconto', 0))
    total_final = subtotal_geral - desconto

    context = {
        'user': request.user,
        'profile': profile,
        'carrinho': carrinho,
        'subtotal_geral': subtotal_geral,
        'desconto': desconto,
        'total_final': total_final,
        'endereco_completo': getattr(profile, 'address', 'Nenhum endereço cadastrado'),
    }

    return render(request, 'core/checkout.html', context)


# ==================== SUPORTE - CHAT COM CLIENTES ====================
@login_required
def support_chat(request):
    """Painel de Suporte da Loja - onde você responde os clientes"""
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para acessar o painel de suporte.")
        return redirect('core:home')

    from django.core.cache import cache

    print("🔥 DEBUG SUPORTE - Iniciando support_chat")
    print(f"   Usuário logado: {request.user.username} (ID: {request.user.id}) - is_staff: {request.user.is_staff}")

    # Busca TODOS os usuários que NÃO são staff e NÃO são você
    potential_customers = User.objects.filter(
        is_staff=False
    ).exclude(id=request.user.id)

    print(f"   Total de usuários não-staff encontrados: {potential_customers.count()}")

    final_customers = []
    for user in potential_customers:
        # Filtro extra de segurança
        if user.id == request.user.id or user.is_staff:
            print(f"   ❌ Ignorando (staff ou próprio usuário): {user.username}")
            continue

        has_messages = ChatMessage.objects.filter(user=user).exists()
        status = cache.get(f'user_status_{user.id}', 'offline')

        print(f"   → Usuário: {user.username} | ID: {user.id} | Status: {status} | Tem mensagens: {has_messages}")

        if has_messages or status in ['online', 'ausente']:
            user.current_status = status
            final_customers.append(user)
            print(f"   ✅ ADICIONADO: {user.username}")

    # Ordenação
    status_order = {'online': 0, 'ausente': 1, 'offline': 2}
    final_customers.sort(key=lambda u: status_order.get(getattr(u, 'current_status', 'offline'), 3))

    print(f"✅ FINAL - Total de clientes reais mostrados: {len(final_customers)}")

    context = {
        'customers': final_customers,
        'title': 'Suporte - Chat com Clientes'
    }
    return render(request, 'accounts/suporte.html', context)