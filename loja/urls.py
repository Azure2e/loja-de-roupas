from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importando as views que usamos diretamente
from core.views import (
    admin_gate, 
    create_superuser_view, 
    painel_suporte   # ← NOVA IMPORTAÇÃO
)

# Personalização do painel administrativo
admin.site.site_header = "SuaLoja - Painel Administrativo"
admin.site.site_title = "SuaLoja Admin"
admin.site.index_title = "Gerenciamento da Loja"

urlpatterns = [
    # ===================== PORTA SECRETA =====================
    path('gestao-secreta-jaques-2026/', admin_gate, name='admin_gate'),
    
    # ===================== CRIAR SUPERUSUÁRIO =====================
    path('gestao-secreta-jaques-2026/criar-superusuario/', create_superuser_view, name='create_superuser'),

    # ===================== PAINEL DE SUPORTE DA LOJA =====================
    path('gestao-secreta-jaques-2026/suporte/', painel_suporte, name='painel_suporte'),

    # ===================== PAINEL ADMIN DO DJANGO =====================
    path('gestao-secreta-jaques-2026/admin/', admin.site.urls),

    # ===================== ROTAS NORMAIS DA LOJA =====================
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # ===================== ALLAUTH =====================
    path('accounts/', include('allauth.urls')),
]

# ===================== ARQUIVOS DE MÍDIA (FOTOS DE PERFIL) =====================
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)