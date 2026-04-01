from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Loja de Roupas'

    def ready(self):
        # Importa os signals quando o app for carregado
        import core.signals   # ← Isso ativa os signals automáticos