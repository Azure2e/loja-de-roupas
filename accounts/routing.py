from django.urls import path
from . import consumers

# ===================== WEB SOCKET URLS =====================
websocket_urlpatterns = [
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]