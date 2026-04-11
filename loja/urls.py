from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import admin_gate   # ← Import direto da view

# Personalização do painel
admin.site.site_header = "SuaLoja - Painel Administrativo"
admin.site.site_title = "SuaLoja Admin"
admin.site.index_title = "Gerenciamento da Loja"

urlpatterns = [
    # ===================== PORTA SECRETA (AGORA DIRETA) =====================
    path('gestao-secreta-jaques-2026/', admin_gate, name='admin_gate'),
    path('gestao-secreta-jaques-2026/admin/', admin.site.urls),

    # ===================== ROTAS NORMAIS =====================
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # ===================== ALLAUTH =====================
    path('accounts/', include('allauth.urls')),
]

# ===================== MÍDIA (desenvolvimento) =====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)