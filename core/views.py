from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse

# ==================== IMPORTS ATUALIZADOS ====================
from .models import Produto, Variante, Pedido, Testimonial   # ← Testimonial já está aqui
from accounts.models import OTPCode

import mercadopago
import random
from datetime import timedelta
from django.utils import timezone
from core.utils.whatsapp import enviar_whatsapp

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json


# ==================== PÁGINAS PRINCIPAIS ====================
def home(request):
    # Produtos para mostrar na home (otimizado e limitado)
    produtos = Produto.objects.filter(
        disponivel=True
    ).select_related('categoria').order_by('-criado_em')[:12]

    # Depoimentos ativos (máximo 6 - perfeito para a tela)
    testimonials = Testimonial.objects.filter(
        ativo=True
    ).order_by('-data')[:6]

    context = {
        'produtos': produtos,
        'testimonials': testimonials,   # ← Agora o template depoimentos.html funciona
    }

    return render(request, 'core/home.html', context)


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
    return redirect('core:carrinho')


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
    return redirect('core:carrinho')


def atualizar_quantidade(request, variante_id):
    carrinho = request.session.get('carrinho', {})
    
    if str(variante_id) in carrinho:
        try:
            nova_quantidade = int(request.POST.get('quantidade', 1))
            if nova_quantidade > 0:
                carrinho[str(variante_id)]['quantidade'] = nova_quantidade
                carrinho[str(variante_id)]['subtotal'] = carrinho[str(variante_id)]['preco'] * nova_quantidade
                request.session['carrinho'] = carrinho
                request.session.modified = True
                messages.success(request, 'Quantidade atualizada com sucesso!')
            else:
                messages.error(request, 'A quantidade deve ser pelo menos 1.')
        except ValueError:
            messages.error(request, 'Quantidade inválida.')
    else:
        messages.error(request, 'Item não encontrado no carrinho.')
    
    return redirect('core:carrinho')


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
        return redirect('core:carrinho')
    return redirect('core:carrinho')


# ==================== CHECKOUT (ATUALIZADO COM DEPOIMENTOS) ====================
@login_required(login_url='accounts:login')
def checkout(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('core:home')

    subtotal_geral = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    desconto = request.session.get('desconto', 0)
    total_final = max(subtotal_geral - desconto, 0)
    profile = request.user.profile

    # ✅ Busca os depoimentos ativos (máximo 6)
    testimonials = Testimonial.objects.filter(ativo=True).order_by('-data')[:6]

    return render(request, 'core/checkout.html', {
        'carrinho': carrinho,
        'subtotal_geral': subtotal_geral,
        'desconto': desconto,
        'total_final': total_final,
        'profile': profile,
        'testimonials': testimonials,
    })


# ==================== (TODO O RESTO DO ARQUIVO FICA IGUAL) ====================
# ... todo o código que você já tinha (criar_preferencia_mercadopago, stripe, etc.)

def criar_preferencia_mercadopago(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('core:home')

    if request.method != 'POST':
        messages.error(request, 'Acesso inválido. Use o formulário do checkout.')
        return redirect('core:checkout')

    email = request.POST.get('email', '').strip()
    if not email:
        email = request.user.email if request.user.is_authenticated and request.user.email else 'contato@sualoja.com'

    if '@' not in email or '.' not in email:
        messages.error(request, '⚠️ Por favor, insira um e-mail válido.')
        return redirect('core:checkout')

    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    if total <= 0:
        messages.error(request, 'Valor inválido para pagamento.')
        return redirect('core:carrinho')

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

    payer_name = request.user.get_full_name() or request.user.username or "Jaques Silva"
    first_name = payer_name.split()[0] if payer_name else "Cliente"
    last_name = " ".join(payer_name.split()[1:]) if len(payer_name.split()) > 1 else "Silva"

    phone_data = {}
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if hasattr(profile, 'phone') and profile.phone:
                phone_str = str(profile.phone)
                if phone_str.startswith('+55'):
                    phone_str = phone_str[3:]
                if len(phone_str) >= 10:
                    area_code = phone_str[:2]
                    number = phone_str[2:]
                    phone_data = {"area_code": area_code, "number": number}
        except:
            pass

    preference_data = {
        "items": items,
        "payer": {
            "name": payer_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            **({"phone": phone_data} if phone_data else {}),
        },
        "back_urls": {
            "success": request.build_absolute_uri(reverse('core:checkout_sucesso')),
            "failure": request.build_absolute_uri(reverse('core:checkout_falha')),
            "pending": request.build_absolute_uri(reverse('core:checkout_pendente')),
        },
        "statement_descriptor": "SUALOJA",
        "external_reference": f"pedido-{request.user.id if request.user.is_authenticated else 'guest'}",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        if preference_response.get("status") == 201:
            init_point = preference_response["response"]["init_point"]
            return redirect(init_point)
        else:
            error_msg = preference_response.get("response", preference_response)
            messages.error(request, f'Erro do Mercado Pago: {error_msg}')
            return redirect('core:carrinho')
    except Exception as e:
        print("❌ Erro completo ao criar preferência:", str(e))
        messages.error(request, f'Erro ao gerar pagamento: {str(e)}')
        return redirect('core:carrinho')


# ==================== STRIPE - NOVA ALTERNATIVA ====================
@login_required(login_url='accounts:login')
def criar_sessao_stripe(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('core:home')

    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    if total <= 0:
        messages.error(request, 'Valor inválido para pagamento.')
        return redirect('core:carrinho')

    line_items = []
    for item in carrinho.values():
        line_items.append({
            'price_data': {
                'currency': 'brl',
                'product_data': {
                    'name': item['nome'],
                    'description': f"{item['tamanho']} • {item['cor']}",
                },
                'unit_amount': int(item['preco'] * 100),
            },
            'quantity': item['quantidade'],
        })

    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card', 'pix', 'boleto'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('core:checkout_sucesso')),
            cancel_url=request.build_absolute_uri(reverse('core:checkout_falha')),
            customer_email=request.user.email,
            metadata={'user_id': str(request.user.id)},
        )

        return redirect(checkout_session.url)

    except Exception as e:
        print("❌ Erro Stripe:", str(e))
        messages.error(request, f'Erro ao gerar pagamento com Stripe: {str(e)}')
        return redirect('core:checkout')


# ==================== CHECKOUT SUCESSO / FALHA / PENDENTE ====================
def checkout_sucesso(request):
    if 'carrinho' in request.session:
        del request.session['carrinho']
    if 'desconto' in request.session:
        del request.session['desconto']
    request.session.modified = True
    request.session.save()
    messages.success(request, '✅ Pagamento recebido! Aguardando confirmação.')
    return render(request, 'core/checkout_sucesso.html')


def checkout_falha(request):
    messages.error(request, 'Pagamento recusado. Tente novamente.')
    return render(request, 'core/checkout_falha.html')


def checkout_pendente(request):
    messages.warning(request, 'Pagamento pendente. Aguarde a confirmação.')
    return render(request, 'core/checkout_pendente.html')


@login_required
def confirmacao_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, user=request.user)
    context = {
        'pedido': pedido,
        'pedido_numero': f"20260413-{pedido.id:04d}",
        'user': request.user,
    }
    return render(request, 'core/confirmacao_pedido.html', context)


@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(user=request.user).order_by('-criado_em')
    context = {
        'pedidos': pedidos,
        'total_pedidos': pedidos.count(),
    }
    return render(request, 'core/meus_pedidos.html', context)


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


# ==================== PROTEÇÃO EXTRA DO ADMIN ====================
def admin_gate(request):
    if request.method == 'POST':
        senha_digitada = request.POST.get('senha', '').strip()
       
        if senha_digitada == settings.ADMIN_MASTER_PASSWORD:
            request.session['admin_master_access'] = True
            request.session.save()
            messages.success(request, '✅ Acesso liberado!')
            return redirect('/gestao-secreta-jaques-2026/admin/')
        else:
            messages.error(request, '❌ Senha master incorreta! Tente novamente.')
 
    return render(request, 'core/admin_gate.html')


# ==================== CREATE SUPERUSER (RESTRITO AO DEBUG) ====================
def create_superuser_view(request):
    if not settings.DEBUG:
        return HttpResponse(status=404)

    if request.method == 'POST':
        master_password = request.POST.get('master_password', '').strip()
       
        if master_password == settings.ADMIN_MASTER_PASSWORD:
            username = request.POST.get('username', 'admin')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
           
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                messages.warning(request, f"Usuário '{username}' já existe!")
            else:
                user = User.objects.create_superuser(username=username, email=email, password=password)
                messages.success(request, f"Superusuário '{username}' criado com sucesso!")
                return redirect('/gestao-secreta-jaques-2026/admin/')
        else:
            messages.error(request, "Senha master incorreta!")
 
    return render(request, 'core/create_superuser.html')


@login_required(login_url='accounts:login')
def painel_suporte(request):
    if not request.user.is_staff:
        messages.error(request, '❌ Acesso negado! Apenas a loja pode acessar o painel de suporte.')
        return redirect('core:home')

    User = get_user_model()
    customers = User.objects.filter(
        is_staff=False,
        is_active=True
    ).order_by('-last_login')

    return render(request, 'accounts/suporte.html', {
        'customers': customers,
    })


# ==================== WEBHOOK MERCADO PAGO ====================
@csrf_exempt
def webhook_mercadopago(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if data.get('type') == 'payment':
                payment_id = data.get('data', {}).get('id')
                if payment_id:
                    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                    payment_info = sdk.payment().get(payment_id)
                    if payment_info['status'] == 200:
                        payment = payment_info['response']
                        external_reference = payment.get('external_reference', '')
                        status_mp = payment.get('status')
                        if external_reference and 'pedido-' in external_reference:
                            try:
                                user_id = external_reference.split('-')[1]
                                User = get_user_model()
                                user = User.objects.get(id=user_id)
                                pedido, created = Pedido.objects.get_or_create(
                                    external_reference=external_reference,
                                    defaults={
                                        'user': user,
                                        'total': payment.get('transaction_amount', 0),
                                        'status': 'pendente'
                                    }
                                )
                                if status_mp == 'approved':
                                    pedido.status = 'pago'
                                    pedido.save()
                                    if created:
                                        profile = user.profile
                                        profile.total_pedidos += 1
                                        profile.pontos_fidelidade += 10
                                        profile.ultima_compra = timezone.now()
                                        profile.save()
                                elif status_mp in ['in_process', 'pending']:
                                    pedido.status = 'pendente'
                                    pedido.save()
                                elif status_mp in ['rejected', 'cancelled']:
                                    pedido.status = 'cancelado'
                                    pedido.save()
                            except (User.DoesNotExist, Exception) as e:
                                print(f"Erro ao processar pedido no webhook: {e}")
        except Exception as e:
            print("Erro no webhook Mercado Pago:", str(e))
  
    return HttpResponse(status=200)