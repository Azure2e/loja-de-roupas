# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.models import UserProfile   # ← Import corrigido
from core.views import enviar_boas_vindas


# ==================== SIGNAL: BOAS-VINDAS AO NOVO USUÁRIO ====================
@receiver(post_save, sender=User)
def criar_perfil_e_enviar_boas_vindas(sender, instance, created, **kwargs):
    """Cria o perfil automaticamente e envia mensagem de boas-vindas"""
    if created:  # Só executa quando um novo usuário é criado
        # Cria o perfil do usuário
        UserProfile.objects.get_or_create(user=instance)
        
        # Envia mensagem de boas-vindas via WhatsApp
        enviar_boas_vindas(instance)