"""
ASGI config for loja project.
Configuração completa para WebSocket com Django Channels + segurança.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Define o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loja.settings')

django_asgi_app = get_asgi_application()

# Importa o routing dos WebSockets (core/routing.py)
import core.routing

application = ProtocolTypeRouter({
    # Rotas HTTP normais (páginas, admin, static, etc.)
    "http": django_asgi_app,

    # Rotas WebSocket com proteção de segurança
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                core.routing.websocket_urlpatterns
            )
        )
    ),
})