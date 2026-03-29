from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

# Desregistra o User padrão e registra com perfil
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)