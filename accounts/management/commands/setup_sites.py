import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Comando para setup inicial do site
    Usage: python manage.py setup_site
    """

    help = "Configura o site inicial com grupos, permissões e superusuário"

    def add_arguments(self, parser):
        parser.add_argument(
            "--admin-email",
            type=str,
            default="admin@lopespeinture.com",
            help="Email do superusuário (padrão: admin@lopespeinture.com)",
        )
        parser.add_argument(
            "--admin-password",
            type=str,
            default="admin123",
            help="Senha do superusuário (padrão: admin123)",
        )
        parser.add_argument(
            "--skip-superuser",
            action="store_true",
            help="Pular criação do superusuário",
        )

    def handle(self, *args, **options):
        """Executar setup completo"""

        self.stdout.write(
            self.style.SUCCESS("🚀 INICIANDO SETUP DO SITE LOPES PEINTURE")
        )
        self.stdout.write("=" * 60)

        try:
            # 1. Criar diretórios de mídia
            self.create_media_directories()

            # 2. Configurar grupos e permissões
            self.setup_groups_and_permissions()

            # 3. Criar superusuário
            if not options["skip_superuser"]:
                self.create_superuser(options["admin_email"], options["admin_password"])

            # 4. Verificar configurações
            self.verify_setup()

            self.stdout.write(self.style.SUCCESS("\n✅ SETUP CONCLUÍDO COM SUCESSO!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ ERRO NO SETUP: {e}"))
            raise CommandError(f"Setup falhou: {e}")

    def create_media_directories(self):
        """Criar diretórios necessários para mídia"""

        self.stdout.write("\n📁 Criando diretórios de mídia...")

        directories = [
            settings.MEDIA_ROOT,
            os.path.join(settings.MEDIA_ROOT, "avatars"),
            os.path.join(settings.MEDIA_ROOT, "projects"),
            os.path.join(settings.MEDIA_ROOT, "documents"),
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.stdout.write(f"  ✅ Criado: {directory}")
            else:
                self.stdout.write(f"  ⏭️  Já existe: {directory}")

    def setup_groups_and_permissions(self):
        """Configurar grupos e suas permissões"""

        self.stdout.write("\n👥 Configurando grupos e permissões...")

        # Definir grupos e suas permissões
        groups_config = {
            "CLIENTS": {
                "description": "Clientes da empresa",
                "permissions": [
                    # Permissões básicas para clientes
                    "view_user",
                    "change_user",  # Apenas próprios dados
                    "view_profile",
                    "change_profile",
                ],
            },
            "COLLABORATORS": {
                "description": "Colaboradores e funcionários",
                "permissions": [
                    # Permissões para colaboradores
                    "view_user",
                    "change_user",
                    "view_profile",
                    "change_profile",
                    "add_project",
                    "change_project",
                    "view_project",
                    "delete_project",
                ],
            },
            "ADMINISTRATORS": {
                "description": "Administradores do sistema",
                "permissions": "all",  # Todas as permissões
            },
        }

        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                self.stdout.write(f"  ✅ Grupo criado: {group_name}")
            else:
                self.stdout.write(f"  ⏭️  Grupo já existe: {group_name}")

            # Configurar permissões
            if config["permissions"] == "all":
                # Dar todas as permissões para administradores
                all_permissions = Permission.objects.all()
                group.permissions.set(all_permissions)
                self.stdout.write(f"    🔑 Todas as permissões atribuídas")
            else:
                # Dar permissões específicas
                assigned_permissions = []
                for perm_codename in config["permissions"]:
                    try:
                        permission = Permission.objects.get(codename=perm_codename)
                        group.permissions.add(permission)
                        assigned_permissions.append(perm_codename)
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"    ⚠️  Permissão não encontrada: {perm_codename}"
                            )
                        )

                if assigned_permissions:
                    self.stdout.write(
                        f"    🔑 Permissões atribuídas: {len(assigned_permissions)}"
                    )

    def create_superuser(self, email, password):
        """Criar superusuário administrador"""

        self.stdout.write("\n👑 Configurando superusuário...")

        # Verificar se já existe
        if User.objects.filter(email=email).exists():
            self.stdout.write(f"  ⏭️  Superusuário já existe: {email}")
            return

        try:
            # Criar superusuário
            admin_user = User.objects.create_user(
                email=email,
                password=password,
                first_name="Admin",
                last_name="LOPES PEINTURE",
                account_type="ADMINISTRATOR",
            )

            # Configurar como superusuário
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

            # Adicionar ao grupo de administradores
            admin_group = Group.objects.get(name="ADMINISTRATORS")
            admin_user.groups.add(admin_group)

            self.stdout.write(f"  ✅ Superusuário criado: {email}")
            self.stdout.write(f"  🔐 Senha: {password}")
            self.stdout.write(
                self.style.WARNING("  ⚠️  MUDE A SENHA APÓS O PRIMEIRO LOGIN!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Erro ao criar superusuário: {e}"))

    def verify_setup(self):
        """Verificar se o setup foi executado corretamente"""

        self.stdout.write("\n🔍 Verificando configurações...")

        # Verificar grupos
        expected_groups = ["CLIENTS", "COLLABORATORS", "ADMINISTRATORS"]
        for group_name in expected_groups:
            if Group.objects.filter(name=group_name).exists():
                group = Group.objects.get(name=group_name)
                perm_count = group.permissions.count()
                self.stdout.write(f"  ✅ {group_name}: {perm_count} permissões")
            else:
                self.stdout.write(f"  ❌ Grupo não encontrado: {group_name}")

        # Verificar superusuário
        admin_count = User.objects.filter(is_superuser=True).count()
        self.stdout.write(f"  ✅ Superusuários: {admin_count}")

        # Verificar diretórios
        if os.path.exists(settings.MEDIA_ROOT):
            self.stdout.write(f"  ✅ Diretório de mídia: {settings.MEDIA_ROOT}")
        else:
            self.stdout.write(f"  ❌ Diretório de mídia não encontrado")

        self.stdout.write("\n📊 Estatísticas:")
        self.stdout.write(f"  👥 Total de usuários: {User.objects.count()}")
        self.stdout.write(f"  🏷️  Total de grupos: {Group.objects.count()}")
        self.stdout.write(f"  🔑 Total de permissões: {Permission.objects.count()}")
