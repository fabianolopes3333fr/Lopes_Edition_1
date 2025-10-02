from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Cliente


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def criar_cliente_automatico(sender, instance, created, **kwargs):
    """
    Criar automaticamente um cliente quando um usuário se registra
    """
    if created and hasattr(instance, 'account_type') and instance.account_type == 'CLIENT':
        # Verificar se já não existe um cliente para este usuário
        if not hasattr(instance, 'cliente'):
            try:
                Cliente.criar_de_usuario(instance)
            except Exception as e:
                # Log do erro mas não quebrar o registro
                print(f"Erro ao criar cliente automaticamente: {e}")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def atualizar_cliente_de_usuario(sender, instance, **kwargs):
    """
    Atualizar informações do cliente quando o usuário é modificado
    """
    if hasattr(instance, 'cliente'):
        cliente = instance.cliente
        # Atualizar informações básicas se estavam vazias
        if not cliente.nom or cliente.nom == 'Nome':
            cliente.nom = instance.last_name or 'Nome'
        if not cliente.prenom:
            cliente.prenom = instance.first_name or ''
        if not cliente.email:
            cliente.email = instance.email or ''

        cliente.save()
