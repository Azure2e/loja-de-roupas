# core/routing.py
from django.urls import path
from . import consumers

# ===================== WEB SOCKET URLS =====================
websocket_urlpatterns = [
    # Notificações (sino no navbar)
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),

    # Status Online / Ausente / Offline
    path('ws/online/', consumers.OnlineStatusConsumer.as_asgi()),

    # Chat do Cliente (lado do usuário)
    path('ws/chat/', consumers.SupportChatConsumer.as_asgi()),

    # Chat do Painel da Loja (lado do suporte)
    path('ws/support/', consumers.StoreSupportConsumer.as_asgi()),
]