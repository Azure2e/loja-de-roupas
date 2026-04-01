from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Produto, Variante, Pedido
from accounts.models import OTPCode
import mercadopago
import random
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from core.utils.whatsapp import enviar_whatsapp


# ==================== PÁGINAS PRINCIPAIS ====================
def home(request):
    produtos = Produto.objects.filter(disponivel=True)
    return render(request, 'core/home.html', {'produtos': produtos})


def detalhe_produto(request, slug):
    produto = get_object_or_404(Produto, slug=slug)
    variantes = produto.variantes.all()
    return render(request, 'core/detalhe_produto.html', {
        'produto': produto,
        'variantes': variantes
    })


def adicionar_ao_carrinho(request, variante_id):
    variante = get_object_or_404(Variante, id=variante_id)
    carrinho = request.session.get('carrinho', {})

    if str(variante_id) in carrinho:
        carrinho[str(variante_id)]['quantidade'] += 1
    else:
        carrinho[str(variante_id)] = {
            'nome': variante.produto.nome,
            'tamanho': variante.tamanho,
            'cor': variante.cor,
            'preco': float(variante.preco_final),
            'quantidade': 1,
            'variante_id': variante_id
        }

    request.session['carrinho'] = carrinho
    messages.success(request, f'{variante.produto.nome} ({variante.tamanho} - {variante.cor}) adicionado ao carrinho!')
    return redirect('core:ver_carrinho')


def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    for item in carrinho.values():
        item['subtotal'] = item['preco'] * item['quantidade']
    
    subtotal_geral = sum(item['subtotal'] for item in carrinho.values())
    desconto = request.session.get('desconto', 0)
    total_final = max(subtotal_geral - desconto, 0)
    
    return render(request, 'core/carrinho.html', {
        'carrinho': carrinho,
        'subtotal_geral': subtotal_geral,
        'desconto': desconto,
        'total_final': total_final
    })


def remover_do_carrinho(request, variante_id):
    carrinho = request.session.get('carrinho', {})
    if str(variante_id) in carrinho:
        del carrinho[str(variante_id)]
        request.session['carrinho'] = carrinho
        messages.success(request, 'Item removido do carrinho!')
    return redirect('core:ver_carrinho')


def aplicar_desconto(request):
    if request.method == 'POST':
        codigo = request.POST.get('cupom', '').strip().upper()
        descontos = {
            'DESCONTO10': 10.00,
            'BLACK10': 15.00,
            'PRIME20': 20.00,
            'ROUPA15': 0.15,
        }
        if codigo in descontos:
            valor = descontos[codigo]
            subtotal = sum(item['preco'] * item['quantidade'] for item in request.session.get('carrinho', {}).values())
            desconto = subtotal * valor if valor < 1 else valor
            request.session['desconto'] = round(desconto, 2)
            messages.success(request, f'Cupom {codigo} aplicado!')
        else:
            messages.error(request, 'Cupom inválido ou expirado!')
        return redirect('core:ver_carrinho')
    return redirect('core:ver_carrinho')


# ==================== CHECKOUT PROTEGIDO ====================
@login_required(login_url='accounts:login')
def checkout(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('core:home')
    
    subtotal_geral = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    desconto = request.session.get('desconto', 0)
    total_final = max(subtotal_geral - desconto, 0)
    
    return render(request, 'core/checkout.html', {
        'carrinho': carrinho,
        'subtotal_geral': subtotal_geral,
        'desconto': desconto,
        'total_final': total_final
    })


# ==================== MERCADO PAGO ====================
def criar_preferencia_mercadopago(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('core:home')

    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    if total <= 0:
        messages.error(request, 'Valor inválido para pagamento.')
        return redirect('core:ver_carrinho')

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    items = []
    for item in carrinho.values():
        items.append({
            "title": item['nome'],
            "description": f"{item['tamanho']} - {item['cor']}",
            "quantity": item['quantidade'],
            "unit_price": float(item['preco']),
            "currency_id": "BRL",
        })

    preference_data = {
        "items": items,
        "back_urls": {
            "success": "http://127.0.0.1:8000/checkout/sucesso/",
            "failure": "http://127.0.0.1:8000/checkout/falha/",
            "pending": "http://127.0.0.1:8000/checkout/pendente/",
        },
        "statement_descriptor": "SUALOJA",
        "external_reference": f"pedido-{request.user.id if request.user.is_authenticated else 'guest'}",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        print("✅ Resposta completa do Mercado Pago:", preference_response)

        if preference_response.get("status") == 201:
            init_point = preference_response["response"]["init_point"]
            return redirect(init_point)
        else:
            error_msg = preference_response.get("response", preference_response)
            messages.error(request, f'Erro do Mercado Pago: {error_msg}')
            return redirect('core:ver_carrinho')

    except Exception as e:
        print("❌ Erro completo ao criar preferência:", str(e))
        messages.error(request, f'Erro ao gerar pagamento: {str(e)}')
        return redirect('core:ver_carrinho')


# ==================== CHECKOUT SUCESSO - COM FIDELIDADE AUTOMÁTICA ====================
def checkout_sucesso(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    # ==================== CRIAÇÃO DO PEDIDO + FIDELIDADE ====================
    if request.user.is_authenticated and carrinho:
        # Cria o pedido no banco
        pedido = Pedido.objects.create(
            user=request.user,
            total=total,
            status='pago'
        )

        # Atualiza fidelidade automaticamente
        profile = request.user.profile
        profile.total_pedidos += 1
        profile.pontos_fidelidade += 10          # 10 pontos por compra
        profile.ultima_compra = timezone.now()
        profile.save()

        # Mensagens automáticas de fidelidade
        if profile.total_pedidos == 3:
            messages.success(request, '🎉 Parabéns! Você agora é cliente Fiel e ganhou 10% OFF na próxima compra!')
        elif profile.total_pedidos >= 6:
            messages.success(request, '👑 Você é VIP! Ganhou 15% OFF na próxima compra!')

    # Limpa o carrinho
    request.session['carrinho'] = {}
    request.session['desconto'] = 0

    messages.success(request, 'Pagamento aprovado com sucesso! 🎉')

    return render(request, 'core/checkout_sucesso.html')


def checkout_falha(request):
    messages.error(request, 'Pagamento recusado. Tente novamente.')
    return render(request, 'core/checkout_falha.html')


def checkout_pendente(request):
    messages.warning(request, 'Pagamento pendente. Aguarde a confirmação.')
    return render(request, 'core/checkout_pendente.html')


# ==================== OTP - VALIDAÇÃO POR TELEFONE ====================
def gerar_otp(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if not phone:
            messages.error(request, 'Número de telefone é obrigatório.')
            return render(request, 'core/gerar_otp.html')

        code = str(random.randint(100000, 999999))

        OTPCode.objects.create(
            user=request.user if request.user.is_authenticated else None,
            phone=phone,
            code=code
        )

        mensagem = f"Seu código de verificação da SuaLoja é: {code}\nVálido por 5 minutos."
        sucesso = enviar_whatsapp(phone, mensagem)

        if sucesso:
            messages.success(request, 'Código enviado para o seu WhatsApp!')
            request.session['otp_phone'] = phone
            return redirect('core:verificar_otp')
        else:
            messages.error(request, 'Erro ao enviar código.')

    return render(request, 'core/gerar_otp.html')


def verificar_otp(request):
    if request.method == 'POST':
        phone = request.session.get('otp_phone')
        code_digitado = request.POST.get('code')

        otp = OTPCode.objects.filter(
            phone=phone,
            code=code_digitado,
            is_used=False,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).first()

        if otp:
            otp.is_used = True
            otp.save()
            messages.success(request, 'Telefone verificado com sucesso!')
            return redirect('core:home')
        else:
            messages.error(request, 'Código inválido ou expirado.')

    return render(request, 'core/verificar_otp.html')


# ==================== MARKETING POR WHATSAPP ====================
def enviar_boas_vindas(user):
    if not hasattr(user, 'profile') or not user.profile.phone:
        return False
    mensagem = f"""
Olá {user.first_name or user.username}! 👋

Bem-vindo(a) à SuaLoja! 🛍️
Use o cupom **BEMVINDO15** e ganhe 15% OFF na sua primeira compra.

Aproveite!
    """
    return enviar_whatsapp(str(user.profile.phone), mensagem.strip())
# ==================== PROTEÇÃO EXTRA DO ADMIN (Senha Master) ====================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

def admin_gate(request):
    if request.method == 'POST':
        senha_digitada = request.POST.get('master_password', '')
        
        if senha_digitada == settings.ADMIN_MASTER_PASSWORD:
            request.session['admin_master_access'] = True
            messages.success(request, '✅ Acesso ao Admin liberado!')
            return redirect('admin:login')   # ou 'gestao-secreta-jaques-2026/admin/'
        else:
            messages.error(request, '❌ Senha master incorreta!')
    
    return render(request, 'core/admin_gate.html')