from django.apps import AppConfig


class OrcamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orcamentos'

    def ready(self):
        """Importar signals quando a aplicação estiver pronta"""
        import orcamentos.signals
