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

    async def disconnect(self, close_code):
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


# ===================== STATUS ONLINE / AUSENTE / OFFLINE =====================
class OnlineStatusConsumer(AsyncWebsocketConsumer):
    """Consumer para status Online / Ausente / Offline em tempo real"""

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
        await self.set_user_status('online')

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            await self.set_user_status('offline')

    async def receive(self, text_data):
        data = json.loads(text_data)
        status = data.get('status')

        if status in ['online', 'ausente', 'offline']:
            await self.set_user_status(status)

    async def set_user_status(self, status: str):
        await database_sync_to_async(cache.set)(
            f"user_status_{self.user.id}", status, timeout=300
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_status_message',
                'user_id': self.user.id,
                'status': status
            }
        )

    async def online_status_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_status',
            'user_id': event['user_id'],
            'status': event['status']
        }))


# ===================== CHAT CLIENTE =====================
class SupportChatConsumer(AsyncWebsocketConsumer):
    """Chat em tempo real — lado do CLIENTE"""

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

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_chat_history(self):
        messages = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages
        }))

    @database_sync_to_async
    def get_chat_history(self):
        messages = ChatMessage.objects.filter(
            user=self.user
        ).order_by('created_at')
        return [{
            'id': m.id,
            'message': m.message,
            'is_from_store': m.is_from_store,
            'time': m.created_at.strftime('%H:%M')
        } for m in messages]

    async def receive(self, text_data):
        """Cliente enviou mensagem"""
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        if not message_text:
            return

        message = await self.save_message(self.user, message_text, is_from_store=False)

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
    def save_message(self, user, message_text, is_from_store=False):
        return ChatMessage.objects.create(
            user=user,
            message=message_text,
            is_from_store=is_from_store
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'is_from_store': event['is_from_store'],
            'time': event['time']
        }))

        # Se a loja respondeu → cria notificação automática para o cliente
        if event.get('is_from_store'):
            await self.create_notification(event['message'])

    @database_sync_to_async
    def create_notification(self, message_text):
        Notification.objects.create(
            user=self.user,
            title="💬 Resposta da Loja",
            message=message_text,
            icon="comment-dots"
        )


# ===================== CHAT PAINEL DE SUPORTE (LOJA) =====================
class StoreSupportConsumer(AsyncWebsocketConsumer):
    """Chat em tempo real — lado da LOJA (painel de suporte)"""

    async def connect(self):
        self.user = self.scope.get("user")
        if self.user is None or self.user.is_anonymous:
            await self.close()
            return

        self.customer_id = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.customer_id:
            await self.channel_layer.group_discard(
                f"support_chat_{self.customer_id}",
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Loja clicou em um cliente → entra na sala dele
        if data.get('type') == 'join_room':
            customer_id = data.get('customer_id')
            if not customer_id:
                return

            # Sai da sala anterior
            if self.customer_id:
                await self.channel_layer.group_discard(
                    f"support_chat_{self.customer_id}",
                    self.channel_name
                )

            self.customer_id = customer_id

            await self.channel_layer.group_add(
                f"support_chat_{self.customer_id}",
                self.channel_name
            )

            await self.send_chat_history()
            return

        # Loja enviou mensagem
        message_text = data.get('message', '').strip()
        if not message_text or not self.customer_id:
            return

        customer = await self.get_customer()
        if not customer:
            return

        message = await self.save_message(customer, message_text)

        await self.channel_layer.group_send(
            f"support_chat_{self.customer_id}",
            {
                'type': 'chat_message',
                'message': message.message,
                'is_from_store': True,
                'time': message.created_at.strftime('%H:%M')
            }
        )

    async def send_chat_history(self):
        messages = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages
        }))

    @database_sync_to_async
    def get_customer(self):
        try:
            return User.objects.get(id=self.customer_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_chat_history(self):
        messages = ChatMessage.objects.filter(
            user_id=self.customer_id
        ).order_by('created_at')
        return [{
            'id': m.id,
            'message': m.message,
            'is_from_store': m.is_from_store,
            'time': m.created_at.strftime('%H:%M')
        } for m in messages]

    @database_sync_to_async
    def save_message(self, customer, message_text):
        return ChatMessage.objects.create(
            user=customer,
            message=message_text,
            is_from_store=True
        )

    async def chat_message(self, event):
        """Recebe broadcast da sala e envia para o painel"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'is_from_store': event['is_from_store'],
            'time': event['time']
        }))