from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import da view de proteção do admin
from core.views import admin_gate

# ==================== CONFIGURAÇÃO DE SEGURANÇA DO ADMIN ====================
admin.site.site_header = "SuaLoja - Painel Administrativo"
admin.site.site_title = "SuaLoja Admin"
admin.site.index_title = "Gerenciamento da Loja"

urlpatterns = [
    # URL SECRETA + Senha Master
    path('gestao-secreta-jaques-2026/', admin_gate, name='admin_gate'),
    path('gestao-secreta-jaques-2026/admin/', admin.site.urls),

    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    
    # Axes (proteção força bruta) - comentado temporariamente para fazer as migrações
    # path('axes/', include('axes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)