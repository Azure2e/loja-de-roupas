from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import admin_gate

admin.site.site_header = "SuaLoja - Painel Administrativo"
admin.site.site_title = "SuaLoja Admin"
admin.site.index_title = "Gerenciamento da Loja"

urlpatterns = [
    # Admin protegido
    path('gestao-secreta-jaques-2026/', admin_gate, name='admin_gate'),
    path('gestao-secreta-jaques-2026/admin/', admin.site.urls),

    # Suas URLs personalizadas (colocadas ANTES do allauth)
    path('accounts/', include('accounts.urls')),

    # Allauth (Google etc.)
    path('accounts/', include('allauth.urls')),

    # URLs da loja
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)