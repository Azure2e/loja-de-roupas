from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ==================== URLS PRINCIPAIS DA LOJA ====================
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),           # rotas da loja (home, produtos, carrinho, etc)
    path('accounts/', include('accounts.urls')),  # rotas de login, cadastro e reset de senha
]

# ==================== SERVIR ARQUIVOS DE MÍDIA (IMAGENS DOS PRODUTOS) ====================
# Apenas em modo desenvolvimento (DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)