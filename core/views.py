from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Produto, Variante, Pedido
from accounts.models import OTPCode

import mercadopago
import random
import json
from datetime import timedelta
from core.utils.whatsapp import enviar_whatsapp


# ==================== HOME ====================
def home(request):
    produtos = Produto.objects.filter(disponivel=True)
    return render(request, 'core/home.html', {'produtos': produtos})


# ==================== PRODUTO ====================
def detalhe_produto(request, slug):
    produto = get_object_or_404(Produto, slug=slug)
    return render(request, 'core/detalhe_produto.html', {
        'produto': produto,
        'variantes': produto.variantes.all()
    })


# ==================== CARRINHO ====================
def adicionar_ao_carrinho(request, variante_id):
    variante = get_object_or_404(Variante, id=variante_id)
    carrinho = request.session.get('carrinho', {})

    item = carrinho.get(str(variante_id), {
        'nome': variante.produto.nome,
        'tamanho': variante.tamanho,
        'cor': variante.cor,
        'preco': float(variante.preco_final),
        'quantidade': 0,
        'variante_id': variante_id
    })

    item['quantidade'] += 1
    carrinho[str(variante_id)] = item

    request.session['carrinho'] = carrinho
    request.session.modified = True

    messages.success(request, "Produto adicionado ao carrinho!")
    return redirect('core:carrinho')


def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})

    for item in carrinho.values():
        item['subtotal'] = item['preco'] * item['quantidade']

    subtotal = sum(item['subtotal'] for item in carrinho.values())
    desconto = request.session.get('desconto', 0)

    return render(request, 'core/carrinho.html', {
        'carrinho': carrinho,
        'subtotal_geral': subtotal,
        'desconto': desconto,
        'total_final': max(subtotal - desconto, 0)
    })


def remover_do_carrinho(request, variante_id):
    carrinho = request.session.get('carrinho', {})

    if str(variante_id) in carrinho:
        del carrinho[str(variante_id)]
        request.session['carrinho'] = carrinho
        request.session.modified = True

    return redirect('core:carrinho')


def atualizar_quantidade(request, variante_id):
    carrinho = request.session.get('carrinho', {})

    if str(variante_id) in carrinho:
        try:
            qnt = int(request.POST.get('quantidade', 1))

            if qnt > 0:
                carrinho[str(variante_id)]['quantidade'] = qnt
                request.session.modified = True
                messages.success(request, "Quantidade atualizada!")
            else:
                messages.error(request, "Quantidade inválida.")
        except:
            messages.error(request, "Erro ao atualizar.")

    return redirect('core:carrinho')


# ==================== CUPOM ====================
def aplicar_desconto(request):
    if request.method == "POST":
        codigo = request.POST.get("cupom", "").upper()

        descontos = {
            "DESCONTO10": 10,
            "BLACK10": 15,
            "PRIME20": 20,
            "ROUPA15": 0.15,
        }

        carrinho = request.session.get('carrinho', {})
        subtotal = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

        if codigo in descontos:
            valor = descontos[codigo]
            desconto = subtotal * valor if valor < 1 else valor
            request.session['desconto'] = round(desconto, 2)
            messages.success(request, f"Cupom {codigo} aplicado!")
        else:
            messages.error(request, "Cupom inválido!")

    return redirect('core:carrinho')


# ==================== CHECKOUT ====================
@login_required(login_url='accounts:login')
def checkout(request):
    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        messages.warning(request, "Carrinho vazio!")
        return redirect('core:home')

    subtotal = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    desconto = request.session.get('desconto', 0)

    return render(request, 'core/checkout.html', {
        'carrinho': carrinho,
        'subtotal_geral': subtotal,
        'desconto': desconto,
        'total_final': max(subtotal - desconto, 0),
        'profile': request.user.profile
    })


# ==================== MERCADO PAGO (CORRIGIDO HTTPS) ====================
def criar_preferencia_mercadopago(request):
    if request.method != "POST":
        return redirect('core:checkout')

    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        return redirect('core:home')

    email = request.POST.get("email")
    base_url = request.build_absolute_uri('/').replace("http://", "https://").rstrip('/')

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    items = [
        {
            "title": item['nome'],
            "quantity": item['quantidade'],
            "unit_price": float(item['preco']),
            "currency_id": "BRL",
        }
        for item in carrinho.values()
    ]

    preference = {
        "items": items,
        "payer": {"email": email},
        "back_urls": {
            "success": f"{base_url}/checkout/sucesso/",
            "failure": f"{base_url}/checkout/falha/",
            "pending": f"{base_url}/checkout/pendente/",
        },
        "external_reference": f"pedido-{request.user.id if request.user.is_authenticated else 'guest'}"
    }

    response = sdk.preference().create(preference)

    if response.get("status") == 201:
        return redirect(response["response"]["init_point"])

    messages.error(request, "Erro no pagamento")
    return redirect('core:carrinho')


# ==================== PAGAMENTO ====================
def checkout_sucesso(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    if request.user.is_authenticated and carrinho:
        pedido = Pedido.objects.create(user=request.user, total=total, status='pago')

        profile = request.user.profile
        profile.total_pedidos += 1
        profile.pontos_fidelidade += 10
        profile.save()

        request.session.flush()
        return redirect('core:confirmacao_pedido', pedido_id=pedido.id)

    return render(request, 'core/checkout_sucesso.html')


def checkout_falha(request):
    messages.error(request, "Pagamento falhou!")
    return render(request, 'core/checkout_falha.html')


def checkout_pendente(request):
    messages.warning(request, "Pagamento pendente!")
    return render(request, 'core/checkout_pendente.html')


# ==================== PEDIDOS ====================
@login_required
def confirmacao_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, user=request.user)

    return render(request, 'core/confirmacao_pedido.html', {
        'pedido': pedido,
        'pedido_numero': f"2026-{pedido.id}"
    })


@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(user=request.user).order_by('-criado_em')

    return render(request, 'core/meus_pedidos.html', {
        'pedidos': pedidos
    })


# ==================== SUPORTE ====================
@login_required
def painel_suporte(request):
    if not request.user.is_staff:
        messages.error(request, "Acesso negado")
        return redirect('core:home')

    User = get_user_model()
    customers = User.objects.filter(is_staff=False, is_active=True).order_by('-last_login')

    return render(request, 'accounts/suporte.html', {
        'customers': customers
    })


# ==================== WEBHOOK ====================
@csrf_exempt
def webhook_mercadopago(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            if data.get("type") == "payment":
                payment_id = data.get("data", {}).get("id")

                if payment_id:
                    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                    payment_info = sdk.payment().get(payment_id)

                    if payment_info["status"] == 200:
                        payment = payment_info["response"]
                        print("Pagamento confirmado:", payment)

        except Exception as e:
            print("Erro webhook:", e)

    return HttpResponse(status=200)