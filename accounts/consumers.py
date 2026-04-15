import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.cache import cache
from .models import Notification, ChatMessage


# ===================== NOTIFICAÇÕES =====================
class NotificationConsumer(AsyncWebsocketConsumer):
    """Consumer para notificações em tempo real (sino)"""

    async def connect(self):
        self.user = self.scope.get("user")
        if self.user is None or self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = f"notifications_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send_unread_notifications()


    async def disconnect(self, close_code): # type: ignore
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )


    async def send_unread_notifications(self):
        notifications = await self.get_unread_notifications()
        await self.send(text_data=json.dumps({
            'type': 'notifications',
            'unread_count': len(notifications),
            'notifications': notifications
        }))


    @database_sync_to_async
    def get_unread_notifications(self):
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


    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event['title'],
            'message': event['message'],
            'icon': event.get('icon', 'bell')
        }))


# ===================== STATUS ONLINE =====================
class OnlineStatusConsumer(AsyncWebsocketConsumer):
    """Consumer para status Online/Offline em tempo real"""

    async def connect(self):
        self.user = self.scope.get("user")
        if self.user is None or self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = "online_users"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.set_user_online(True)


    async def disconnect(self, close_code): # type: ignore
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            await self.set_user_online(False)


    @database_sync_to_async
    def set_user_online(self, is_online):
        cache.set(f"user_online_{self.user.id}", is_online, timeout=300) # type: ignore


# ===================== CHAT ONLINE + INTEGRAÇÃO COM NOTIFICAÇÕES =====================
class SupportChatConsumer(AsyncWebsocketConsumer):
    """Chat em tempo real direto com a loja (integrado com notificações)"""

    async def connect(self):
        self.user = self.scope.get("user")
        if self.user is None or self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = f"support_chat_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send_chat_history()


    async def disconnect(self, close_code): # type: ignore
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def send_chat_history(self):
        messages = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages
        }))


    @database_sync_to_async
    def get_chat_history(self):
        messages = ChatMessage.objects.filter(user=self.user).order_by('created_at')
        return [{
            'id': m.id, # type: ignore
            'message': m.message,
            'is_from_store': m.is_from_store,
            'time': m.created_at.strftime('%H:%M')
        } for m in messages]


    async def receive(self, text_data): # type: ignore
        """Cliente enviou mensagem"""
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        if not message_text:
            return

        message = await self.save_message(message_text, is_from_store=False)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.message,
                'is_from_store': False,
                'time': message.created_at.strftime('%H:%M')
            }
        )


    @database_sync_to_async
    def save_message(self, message_text, is_from_store=False):
        return ChatMessage.objects.create(
            user=self.user,
            message=message_text,
            is_from_store=is_from_store
        )


    async def chat_message(self, event):
        """Recebe mensagem (cliente ou loja)"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'is_from_store': event['is_from_store'],
            'time': event['time']
        }))

        # INTEGRAÇÃO: Se a loja respondeu, cria notificação automática no sino
        if event.get('is_from_store'):
            await self.create_notification(event['message'])


    @database_sync_to_async
    def create_notification(self, message_text):
        """Cria notificação automática para o cliente quando a loja responde"""
        Notification.objects.create(
            user=self.user,
            title="💬 Resposta da Loja",
            message=message_text,
            icon="comment-dots"
        )


    # Permite que a loja envie mensagens pelo painel admin
    async def store_message(self, event):
        message = await self.save_message(event['message'], is_from_store=True)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.message,
                'is_from_store': True,
                'time': message.created_at.strftime('%H:%M')
            }
        )