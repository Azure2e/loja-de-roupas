"""
ASGI config for loja project.
Configuração completa para WebSocket com Django Channels.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Define o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loja.settings')

django_asgi_app = get_asgi_application()

# Importa o routing das notificações WebSocket
import accounts.routing

application = ProtocolTypeRouter({
    # Rotas HTTP normais (páginas, admin, etc.)
    "http": django_asgi_app,

    # Rotas WebSocket (notificações em tempo real)
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                accounts.routing.websocket_urlpatterns
            )
        )
    ),
})