from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Gestion des Comptes"

    def ready(self):
        """Importar signals quando app estiver pronto"""
        import accounts.signals

        # Importar admin personalizado para grupos
        from . import admin_groups
