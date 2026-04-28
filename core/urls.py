from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ==================== PÁGINAS PRINCIPAIS ====================
    path('', views.home, name='home'),
    path('produto/<slug:slug>/', views.detalhe_produto, name='detalhe_produto'),

    # ==================== CARRINHO ====================
    path('adicionar/<int:variante_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/', views.ver_carrinho, name='carrinho'),
    path('remover/<int:variante_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('atualizar/<int:variante_id>/', views.atualizar_quantidade, name='atualizar_quantidade'),
    path('aplicar-desconto/', views.aplicar_desconto, name='aplicar_desconto'),

    # ==================== CHECKOUT ====================
    path('checkout/', views.checkout, name='checkout'),
    path('criar-preferencia/', views.criar_preferencia_mercadopago, name='criar_preferencia_mercadopago'),

    # ==================== RETORNO DO MERCADO PAGO ====================
    path('checkout/sucesso/', views.checkout_sucesso, name='checkout_sucesso'),
    path('checkout/falha/', views.checkout_falha, name='checkout_falha'),
    path('checkout/pendente/', views.checkout_pendente, name='checkout_pendente'),

    # ==================== CONFIRMAÇÃO DE PEDIDO ====================
    path('confirmacao/<int:pedido_id>/', views.confirmacao_pedido, name='confirmacao_pedido'),

    # ==================== OUTRAS PÁGINAS ====================
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('gerar-otp/', views.gerar_otp, name='gerar_otp'),
    path('verificar-otp/', views.verificar_otp, name='verificar_otp'),

    # ==================== DEPOIMENTOS ====================
    path('enviar-depoimento/', views.enviar_depoimento, name='enviar_depoimento'),
    path('depoimentos/', views.depoimentos, name='depoimentos'),   # ← ADICIONADO AQUI

    # ==================== WEBHOOK ====================
    path('webhook/mercadopago/', views.webhook_mercadopago, name='webhook_mercadopago'),
]