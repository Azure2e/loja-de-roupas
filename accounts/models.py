from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==================== PERFIL DO USUÁRIO ====================
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # ==================== FOTO DE PERFIL ====================
    picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name="Foto de Perfil"
    )

    # Dados básicos
    nome_completo = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nome Completo"
    )

    # Telefone com validação automática
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name="Telefone / WhatsApp",
        help_text="Exemplo: +5511999999999 (Brasil) ou +59171234567 (Bolívia)"
    )

    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Endereço Completo"
    )

    # Sexo
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Prefiro não informar'),
    ]
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        blank=True,
        verbose_name="Sexo"
    )

    # Estado Civil
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Solteiro(a)'),
        ('C', 'Casado(a)'),
        ('D', 'Divorciado(a)'),
        ('V', 'Viúvo(a)'),
        ('U', 'União Estável'),
        ('N', 'Prefiro não informar'),
    ]
    estado_civil = models.CharField(
        max_length=1,
        choices=ESTADO_CIVIL_CHOICES,
        blank=True,
        verbose_name="Estado Civil"
    )

    # ==================== FIDELIDADE ====================
    total_pedidos = models.PositiveIntegerField(default=0, verbose_name="Total de Pedidos")
    pontos_fidelidade = models.PositiveIntegerField(default=0, verbose_name="Pontos de Fidelidade")
    ultima_compra = models.DateTimeField(null=True, blank=True, verbose_name="Última Compra")

    @property
    def nivel_fidelidade(self):
        if self.total_pedidos >= 6:
            return "VIP 👑"
        elif self.total_pedidos >= 3:
            return "Fiel ⭐"
        else:
            return "Iniciante"

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"


# ==================== OTP (CÓDIGO DE VERIFICAÇÃO) ====================
class OTPCode(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP para {self.user.username if self.user else 'Anônimo'} - {self.code}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Código OTP"
        verbose_name_plural = "Códigos OTP"


# ==================== NOTIFICAÇÕES REAIS ====================
class Notification(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    title = models.CharField(max_length=100, verbose_name="Título")
    message = models.TextField(verbose_name="Mensagem")
    icon = models.CharField(
        max_length=50, 
        default='bell', 
        verbose_name="Ícone"
    )
    is_read = models.BooleanField(default=False, verbose_name="Lida")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"{self.title} - {self.user.username}"


# ==================== SINAL: Criar perfil automaticamente ====================
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Atualiza o perfil caso o usuário já exista
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)