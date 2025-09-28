import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import User, AccountType

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def setup_user_profile_and_permissions(sender, instance, created, **kwargs):
    """
    ✅ CORRIGIDO: Configura perfil e permissões apenas na CRIAÇÃO
    """
    if created:  # ✅ IMPORTANTE: Apenas para usuários recém-criados
        try:
            logger.info(f"Configurando usuário recém-criado: {instance.email}")

            # 1. Criar perfil automaticamente
            create_user_profile(instance)

            # 2. Criar grupos se não existirem
            setup_groups_and_permissions()

            # 3. Adicionar usuário ao grupo correto
            add_user_to_group(instance)

            logger.info(f"Configuração completa para {instance.email}")

        except Exception as e:
            logger.error(f"Erro ao configurar usuário {instance.email}: {e}")


def create_user_profile(user):
    """Criar perfil do usuário"""
    try:
        from profiles.models import Profile

        # ✅ VERIFICAR: Se já existe perfil
        if hasattr(user, "profile") and user.profile:
            logger.info(f"Perfil já existe para {user.email}")
            return

        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            logger.info(f"Perfil criado para {user.email}")
        else:
            logger.info(f"Perfil já existia para {user.email}")

    except Exception as e:
        logger.error(f"Erro ao criar perfil para {user.email}: {e}")


def setup_groups_and_permissions():
    """Cria grupos e configura permissões"""
    try:
        # Criar grupos se não existirem
        clients_group, created = Group.objects.get_or_create(name="CLIENTS")
        if created:
            logger.info("Grupo CLIENTS criado")

        collaborators_group, created = Group.objects.get_or_create(name="COLLABORATORS")
        if created:
            logger.info("Grupo COLLABORATORS criado")

        admins_group, created = Group.objects.get_or_create(name="ADMINISTRATORS")
        if created:
            logger.info("Grupo ADMINISTRATORS criado")

        # Configurar permissões (opcional - pode ser feito via admin)
        setup_basic_permissions(clients_group, collaborators_group, admins_group)

    except Exception as e:
        logger.error(f"Erro ao configurar grupos: {e}")


def setup_basic_permissions(clients_group, collaborators_group, admins_group):
    """Configurar permissões básicas"""
    try:
        # ✅ SIMPLIFICADO: Apenas permissões básicas para evitar erros

        # Clients - podem ver próprio perfil
        client_perms = ["view_profile", "change_profile"]
        for perm_code in client_perms:
            try:
                perm = Permission.objects.get(codename=perm_code)
                clients_group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass  # Ignorar se não existir

        # Collaborators - herdam de clients + podem ver usuários
        collaborators_group.permissions.set(clients_group.permissions.all())
        collab_perms = ["view_user", "add_project", "change_project", "view_project"]
        for perm_code in collab_perms:
            try:
                perm = Permission.objects.get(codename=perm_code)
                collaborators_group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass

        # Admins - todas as permissões (configurado automaticamente pelo Django)

    except Exception as e:
        logger.warning(f"Erro ao configurar permissões: {e}")


def add_user_to_group(user):
    """✅ CORRIGIDO: Adiciona usuário ao grupo SEM salvar (evita recursão)"""
    try:
        # ✅ IMPORTANTE: Não usar user.save() aqui para evitar recursão

        # Limpar grupos atuais
        user.groups.clear()

        if user.account_type == AccountType.CLIENT:
            try:
                group = Group.objects.get(name="CLIENTS")
                user.groups.add(group)
                logger.info(f"Usuário {user.email} adicionado ao grupo CLIENTS")
            except Group.DoesNotExist:
                logger.error("Grupo CLIENTS não encontrado")

        elif user.account_type == AccountType.COLLABORATOR:
            try:
                group = Group.objects.get(name="COLLABORATORS")
                user.groups.add(group)

                # ✅ CORRIGIDO: Usar update() para evitar trigger de signals
                User.objects.filter(pk=user.pk).update(is_staff=True)
                logger.info(f"Usuário {user.email} adicionado ao grupo COLLABORATORS")
            except Group.DoesNotExist:
                logger.error("Grupo COLLABORATORS não encontrado")

        elif user.account_type == AccountType.ADMINISTRATOR:
            try:
                group = Group.objects.get(name="ADMINISTRATORS")
                user.groups.add(group)

                # ✅ CORRIGIDO: Usar update() para evitar trigger de signals
                User.objects.filter(pk=user.pk).update(is_staff=True, is_superuser=True)
                logger.info(f"Usuário {user.email} adicionado ao grupo ADMINISTRATORS")
            except Group.DoesNotExist:
                logger.error("Grupo ADMINISTRATORS não encontrado")

    except Exception as e:
        logger.error(f"Erro ao adicionar usuário {user.email} ao grupo: {e}")


# ✅ REMOVIDO: Signal que causava recursão
# O signal de update_user_group_on_type_change foi removido para evitar loops
