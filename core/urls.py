from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ===================== PORTA SECRETA (ACESSO AO ADMIN) =====================
    path('', views.admin_gate, name='admin_gate'),

    # ===================== CRIAR SUPERUSUÁRIO (página temporária) =====================
    path('criar-superusuario/', views.create_superuser_view, name='create_superuser'),

    # ===================== ROTAS NORMAIS DA LOJA =====================
    path('home/', views.home, name='home'),
    path('produto/<slug:slug>/', views.detalhe_produto, name='detalhe_produto'), # type: ignore
    path('adicionar/<int:variante_id>/', views.adicionar_ao_carrinho, name='adicionar_carrinho'),

    # ==================== CARRINHO ====================
    path('carrinho/', views.ver_carrinho, name='carrinho'),
    path('carrinho/remover/<int:variante_id>/', views.remover_do_carrinho, name='remover_carrinho'),
    path('carrinho/atualizar/<int:variante_id>/', views.atualizar_quantidade, name='atualizar_quantidade'),
    path('carrinho/aplicar-desconto/', views.aplicar_desconto, name='aplicar_desconto'),

    # ==================== CHECKOUT ====================
    path('checkout/', views.checkout, name='checkout'),

    # ==================== Mercado Pago ====================
    path('checkout/mercadopago/', views.criar_preferencia_mercadopago, name='mercadopago'),
    path('checkout/sucesso/', views.checkout_sucesso, name='checkout_sucesso'),
    path('checkout/falha/', views.checkout_falha, name='checkout_falha'),
    path('checkout/pendente/', views.checkout_pendente, name='checkout_pendente'),

    # ==================== MEUS PEDIDOS ====================
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),

    # ==================== OTP ====================
    path('gerar-otp/', views.gerar_otp, name='gerar_otp'),
    path('verificar-otp/', views.verificar_otp, name='verificar_otp'),
]