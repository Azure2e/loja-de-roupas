from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import admin_gate

# Personalização do painel administrativo
admin.site.site_header = "SuaLoja - Painel Administrativo"
admin.site.site_title = "SuaLoja Admin"
admin.site.index_title = "Gerenciamento da Loja"

urlpatterns = [
    # ===================== ADMIN PROTEGIDO (URL SECRETA) =====================
    path('gestao-secreta-jaques-2026/', admin_gate, name='admin_gate'),
    path('gestao-secreta-jaques-2026/admin/', admin.site.urls),

    # ===================== SUAS APPS =====================
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # ===================== ALLAUTH (Google, login social, etc.) =====================
    path('accounts/', include('allauth.urls')),
]

# ===================== ARQUIVOS DE MÍDIA (apenas em desenvolvimento) =====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)