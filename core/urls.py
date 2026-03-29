from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('produto/<slug:slug>/', views.detalhe_produto, name='detalhe_produto'),
    path('adicionar/<int:variante_id>/', views.adicionar_ao_carrinho, name='adicionar_carrinho'),
    
    # Carrinho + Desconto
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/remover/<int:variante_id>/', views.remover_do_carrinho, name='remover_carrinho'),
    path('carrinho/aplicar-desconto/', views.aplicar_desconto, name='aplicar_desconto'),   # ← aplicado agora
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
]