# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from accounts.models import UserProfile, Notification

# Import do modelo de Pedido (ajuste o nome se for diferente)
from core.models import Pedido   # ← Certifique-se que o nome do modelo é "Pedido"


# ==================== SINAL: BOAS-VINDAS AO NOVO USUÁRIO ====================
@receiver(post_save, sender=User)
def criar_perfil_e_enviar_boas_vindas(sender, instance, created, **kwargs):
    """Cria o perfil automaticamente e envia mensagem de boas-vindas"""
    if created:
        UserProfile.objects.get_or_create(user=instance)
        # Chama a função de boas-vindas via WhatsApp (se existir)
        try:
            from core.views import enviar_boas_vindas
            enviar_boas_vindas(instance)
        except ImportError:
            pass  # Caso a função ainda não exista


# ==================== SINAL: NOTIFICAÇÃO DE PEDIDO ====================
@receiver(post_save, sender=Pedido)
def criar_notificacao_pedido(sender, instance, created, **kwargs):
    """Cria notificação quando o status do pedido for alterado"""
    if not created:  # Só executa quando o pedido for atualizado (não criado)
        status = instance.status
        mensagem = ""

        if status == 'pago':
            mensagem = f"Seu pedido #{instance.numero_pedido} foi confirmado e pago! ✅"
        elif status == 'enviado':
            mensagem = f"Seu pedido #{instance.numero_pedido} foi enviado! 📦"
        elif status == 'entregue':
            mensagem = f"Seu pedido #{instance.numero_pedido} foi entregue! 🎉"

        if mensagem:
            Notification.objects.create(
                user=instance.user,
                title="Atualização do Pedido",
                message=mensagem,
                icon="bell"
            )