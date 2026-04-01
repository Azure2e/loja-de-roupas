from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('produto/<slug:slug>/', views.detalhe_produto, name='detalhe_produto'),
    path('adicionar/<int:variante_id>/', views.adicionar_ao_carrinho, name='adicionar_carrinho'),
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/remover/<int:variante_id>/', views.remover_do_carrinho, name='remover_carrinho'),
    path('carrinho/aplicar-desconto/', views.aplicar_desconto, name='aplicar_desconto'),
    path('checkout/', views.checkout, name='checkout'),
    
    # ==================== Mercado Pago ====================
    path('checkout/mercadopago/', views.criar_preferencia_mercadopago, name='mercadopago'),
    path('checkout/sucesso/', views.checkout_sucesso, name='checkout_sucesso'),
    path('checkout/falha/', views.checkout_falha, name='checkout_falha'),
    path('checkout/pendente/', views.checkout_pendente, name='checkout_pendente'),

    # ==================== OTP - Validação por Telefone/WhatsApp ====================
    path('gerar-otp/', views.gerar_otp, name='gerar_otp'),
    path('verificar-otp/', views.verificar_otp, name='verificar_otp'),
]