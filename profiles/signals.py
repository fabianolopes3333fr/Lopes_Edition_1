import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """✅ CORRIGIDO: Criar perfil apenas quando usuário é criado"""
    if created:
        try:
            # Importar aqui para evitar circular import
            from .models import Profile

            profile, profile_created = Profile.objects.get_or_create(user=instance)

            if profile_created:
                logger.info(f"Perfil criado automaticamente para {instance.email}")

            # Configurar grupos apenas na criação
            _setup_user_groups(instance)

        except Exception as e:
            logger.error(f"Erro ao criar perfil para {instance.email}: {e}")


def _setup_user_groups(user):
    """✅ NOVO: Configurar grupos do usuário sem causar recursão"""
    try:
        from accounts.models import AccountType

        # Criar grupos se não existirem
        clients_group, _ = Group.objects.get_or_create(name="CLIENTS")
        collaborators_group, _ = Group.objects.get_or_create(name="COLLABORATORS")
        admins_group, _ = Group.objects.get_or_create(name="ADMINISTRATORS")

        # Adicionar ao grupo baseado no account_type
        if user.account_type == AccountType.CLIENT:
            user.groups.add(clients_group)

        elif user.account_type == AccountType.COLLABORATOR:
            user.groups.add(collaborators_group)
            # Usar update() para evitar trigger de signals
            type(user).objects.filter(pk=user.pk).update(is_staff=True)

        elif user.account_type == AccountType.ADMINISTRATOR:
            user.groups.add(admins_group)
            # Usar update() para evitar trigger de signals
            type(user).objects.filter(pk=user.pk).update(
                is_staff=True, is_superuser=True
            )

        logger.info(f"Grupos configurados para {user.email}")

    except Exception as e:
        logger.error(f"Erro ao configurar grupos para {user.email}: {e}")
