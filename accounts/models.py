from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


# ==================== PERFIL DO USUÁRIO ====================
class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Telefone com validação automática
    phone = PhoneNumberField(
        blank=True, 
        null=True, 
        verbose_name="Telefone / WhatsApp",
        help_text="Exemplo: +5511999999999 (Brasil) ou +59171234567 (Bolívia)"
    )
    
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")

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
            # ==================== FIDELIDADE ====================
    total_pedidos = models.PositiveIntegerField(default=0, verbose_name="Total de Pedidos")
    pontos_fidelidade = models.PositiveIntegerField(default=0, verbose_name="Pontos de Fidelidade")
    ultima_compra = models.DateTimeField(null=True, blank=True)

    @property
    def nivel_fidelidade(self):
        if self.total_pedidos >= 6:
            return "VIP"
        elif self.total_pedidos >= 3:
            return "Fiel"
        else:
            return "Iniciante"