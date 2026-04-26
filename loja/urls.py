from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importando as views do core
from core import views as core_views

# Personalização do painel administrativo
admin.site.site_header = "SuaLoja - Painel Administrativo"
admin.site.site_title = "SuaLoja Admin"
admin.site.index_title = "Gerenciamento da Loja"

urlpatterns = [
    # ===================== PORTA SECRETA =====================
    path('gestao-secreta-jaques-2026/', core_views.admin_gate, name='admin_gate'),
    
    # ===================== CRIAR SUPERUSUÁRIO =====================
    path('gestao-secreta-jaques-2026/criar-superusuario/', core_views.create_superuser_view, name='create_superuser'),

    # ===================== PAINEL DE SUPORTE =====================
    path('gestao-secreta-jaques-2026/suporte/', core_views.painel_suporte, name='painel_suporte'),

    # ===================== ADMIN DJANGO =====================
    path('gestao-secreta-jaques-2026/admin/', admin.site.urls),

    # ===================== ROTAS DA LOJA =====================
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # ===================== ALLAUTH =====================
    path('accounts/', include('allauth.urls')),

    # ===================== STRIPE =====================
    path('criar-sessao-stripe/', core_views.criar_sessao_stripe, name='criar_sessao_stripe'),
]

# ===================== ARQUIVOS DE MÍDIA (só em desenvolvimento) =====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)