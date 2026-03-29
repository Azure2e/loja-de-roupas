from django.db import models
from django.contrib.auth.models import User

# Se quiser adicionar campos extras no futuro (ex: telefone, endereço)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username