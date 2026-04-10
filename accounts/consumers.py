import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user")

        # Rejeita se não estiver logado
        if self.user is None or self.user.is_anonymous:
            await self.close()
            return

        # Grupo único por usuário
        self.room_group_name = f"notifications_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send_unread_notifications()


    async def disconnect(self, close_code):
        """Método chamado quando a conexão WebSocket é fechada"""
        # Sai do grupo de forma segura
        if hasattr(self, 'room_group_name'):
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                # Log ou ignore errors durante desconexão
                pass


    async def send_unread_notifications(self):
        """Envia as notificações não lidas para o cliente"""
        notifications = await self.get_unread_notifications()

        await self.send(text_data=json.dumps({
            'type': 'notifications',
            'unread_count': len(notifications),
            'notifications': notifications
        }))


    @database_sync_to_async
    def get_unread_notifications(self):
        """Busca notificações não lidas do banco"""
        notifications = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).order_by('-created_at')[:10]

        return [{
            'id': n.pk,
            'title': n.title,
            'message': n.message,
            'icon': n.icon,
            'time': n.created_at.strftime('%d/%m %H:%M')
        } for n in notifications]


    # Recebe mensagem enviada do backend
    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event['title'],
            'message': event['message'],
            'icon': event.get('icon', 'bell')
        }))