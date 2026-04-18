from django.urls import path
from . import consumers

# ===================== WEB SOCKET URLS =====================
websocket_urlpatterns = [
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
    path('ws/online/', consumers.OnlineStatusConsumer.as_asgi()),
    path('ws/chat/', consumers.SupportChatConsumer.as_asgi()),      # ← Chat Cliente → Loja
    path('ws/support/', consumers.StoreSupportConsumer.as_asgi()),  # ← Chat Loja → Cliente
]