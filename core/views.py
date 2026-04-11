from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

from .models import Produto, Variante, Pedido
from accounts.models import OTPCode

import mercadopago
import random
from datetime import timedelta
from django.utils import timezone
from core.utils.whatsapp import enviar_whatsapp

# ==================== IMPORTS DO WEBHOOK ====================
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json


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

    return render(request, 'core/checkout.html', {
        'carrinho': carrinho,
        'subtotal_geral': subtotal_geral,
        'desconto': desconto,
        'total_final': total_final,
        'profile': profile,
    })


def criar_preferencia_mercadopago(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('core:home')

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


def checkout_sucesso(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    if request.user.is_authenticated and carrinho:
        pedido = Pedido.objects.create(
            user=request.user,
            total=total,
            status='pago'
        )
        profile = request.user.profile
        profile.total_pedidos += 1
        profile.pontos_fidelidade += 10
        profile.ultima_compra = timezone.now()
        profile.save()

        if profile.total_pedidos == 3:
            messages.success(request, '🎉 Parabéns! Você agora é cliente Fiel!')
        elif profile.total_pedidos >= 6:
            messages.success(request, '👑 Você é VIP!')

    if 'carrinho' in request.session:
        del request.session['carrinho']
    if 'desconto' in request.session:
        del request.session['desconto']
    request.session.modified = True
    request.session.save()

    messages.success(request, '✅ Pagamento aprovado com sucesso! Seu carrinho foi limpo.')
    return render(request, 'core/checkout_sucesso.html')


def checkout_falha(request):
    messages.error(request, 'Pagamento recusado. Tente novamente.')
    return render(request, 'core/checkout_falha.html')


def checkout_pendente(request):
    messages.warning(request, 'Pagamento pendente. Aguarde a confirmação.')
    return render(request, 'core/checkout_pendente.html')


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
            request.session.save()                    # Força salvar a sessão
            messages.success(request, '✅ Acesso liberado!')
            return redirect('/gestao-secreta-jaques-2026/admin/')
        else:
            messages.error(request, '❌ Senha master incorreta! Tente novamente.')
  
    return render(request, 'core/admin_gate.html')


# ==================== CRIAR SUPERUSUÁRIO TEMPORÁRIO ====================
def create_superuser_view(request):
    """Página temporária para criar superusuário (protegida pela senha master)"""
    if request.method == 'POST':
        master_password = request.POST.get('master_password', '').strip()
        
        if master_password == settings.ADMIN_MASTER_PASSWORD:
            username = request.POST.get('username', 'admin')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            
            if User.objects.filter(username=username).exists():
                messages.warning(request, f"Usuário '{username}' já existe!")
            else:
                user = User.objects.create_superuser(username=username, email=email, password=password)
                messages.success(request, f"Superusuário '{username}' criado com sucesso!")
                return redirect('/gestao-secreta-jaques-2026/admin/')
        else:
            messages.error(request, "Senha master incorreta!")
   
    return render(request, 'core/create_superuser.html')


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
                        external_reference = payment.get('external_reference')
                        
                        if external_reference and 'pedido-' in external_reference:
                            try:
                                pedido_id = external_reference.split('-')[1]
                                pedido = Pedido.objects.get(id=pedido_id)
                                
                                status_mp = payment['status']
                                
                                if status_mp == 'approved':
                                    pedido.status = 'pago'
                                    pedido.save()
                                elif status_mp in ['in_process', 'pending']:
                                    pedido.status = 'pendente'
                                    pedido.save()
                                elif status_mp in ['rejected', 'cancelled']:
                                    pedido.status = 'pendente'
                                    pedido.save()
                            except Pedido.DoesNotExist:
                                print(f"Pedido não encontrado: {external_reference}")
        except Exception as e:
            print("Erro no webhook Mercado Pago:", str(e))
   
    return HttpResponse(status=200)