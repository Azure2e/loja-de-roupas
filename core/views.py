from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required   # ← IMPORTADO

from .models import Produto, Variante

# ==================== CARRINHO COM DESCONTO ====================
def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    
    # Calcula subtotal de cada item
    for item in carrinho.values():
        item['subtotal'] = item['preco'] * item['quantidade']
    
    subtotal_geral = sum(item['subtotal'] for item in carrinho.values())
    
    # Desconto (vem da sessão)
    desconto = request.session.get('desconto', 0)
    total_final = max(subtotal_geral - desconto, 0)
    
    return render(request, 'core/carrinho.html', {
        'carrinho': carrinho,
        'subtotal_geral': subtotal_geral,
        'desconto': desconto,
        'total_final': total_final
    })

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
            subtotal = sum(item['preco'] * item['quantidade'] 
                          for item in request.session.get('carrinho', {}).values())
            
            if valor < 1:  # porcentagem
                desconto = subtotal * valor
            else:
                desconto = valor
                
            request.session['desconto'] = round(desconto, 2)
            messages.success(request, f'Cupom {codigo} aplicado! 🎟️')
        else:
            messages.error(request, 'Cupom inválido ou expirado 😢')
        
        return redirect('core:ver_carrinho')
    return redirect('core:ver_carrinho')

# ==================== CHECKOUT SEGURO (PROTEGIDO) ====================
@login_required(login_url='accounts:login')   # ← PROTEÇÃO ADICIONADA
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

# ==================== OUTRAS FUNÇÕES ====================
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
    messages.success(request, f'{variante.produto.nome} adicionado!')
    return redirect('core:ver_carrinho')

def remover_do_carrinho(request, variante_id):
    carrinho = request.session.get('carrinho', {})
    if str(variante_id) in carrinho:
        del carrinho[str(variante_id)]
        request.session['carrinho'] = carrinho
        messages.success(request, 'Item removido!')
    return redirect('core:ver_carrinho')