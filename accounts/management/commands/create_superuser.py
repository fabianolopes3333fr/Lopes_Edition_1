from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
import getpass
import sys

User = get_user_model()


class Command(BaseCommand):
    help = "Criar um superusuário com perfil completo para Lopes Peinture"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, help="Email do superusuário")
        parser.add_argument("--first-name", type=str, help="Prénom do superusuário")
        parser.add_argument("--last-name", type=str, help="Nom do superusuário")
        parser.add_argument(
            "--no-input", action="store_true", help="Não solicitar entrada do usuário"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forçar criação mesmo se já existir superusuário",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "=== Création d'un Super Administrateur - Lopes Peinture ===\n"
            )
        )

        # Verificar se já existe um superuser
        existing_superusers = User.objects.filter(is_superuser=True)
        if existing_superusers.exists() and not options.get("force"):
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Un ou plusieurs super administrateurs existent déjà:"
                )
            )
            for user in existing_superusers:
                self.stdout.write(f"   - {user.email} ({user.get_full_name()})")

            if not options.get("no_input"):
                confirm = input(
                    "\nVoulez-vous créer un autre super administrateur ? (o/N): "
                )
                if confirm.lower() not in ["o", "oui", "y", "yes"]:
                    self.stdout.write(self.style.ERROR("Opération annulée."))
                    return

        try:
            # ✅ CORRIGIDO: Desconectar signals temporariamente para evitar recursão
            post_save.disconnect(sender=User)

            with transaction.atomic():
                # Coletar dados
                email = self._get_email(options)
                first_name = self._get_first_name(options)
                last_name = self._get_last_name(options)
                password = self._get_password(options)

                self.stdout.write("🔨 Création en cours...")

                # ✅ CORRIGIDO: Criar superuser diretamente
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )

                self.stdout.write("✅ Utilisateur créé, configuration des groupes...")

                # ✅ CRIAR GRUPOS MANUALMENTE
                self._setup_groups_manually(user)

                # ✅ CRIAR PERFIL MANUALMENTE
                self._create_profile_manually(user)

                self.stdout.write(
                    self.style.SUCCESS(f"\n🎉 Super administrateur créé avec succès!")
                )
                self._show_user_info(user, email, password)

        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur de validation: {e}"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur lors de la création: {str(e)}")
            )
            if options.get("verbosity", 1) >= 2:
                import traceback

                self.stdout.write(traceback.format_exc())
        finally:
            # ✅ RECONECTAR SIGNALS
            from accounts.signals import setup_user_profile_and_permissions

            post_save.connect(setup_user_profile_and_permissions, sender=User)

    def _setup_groups_manually(self, user):
        """Configurar grupos manualmente"""
        try:
            # Criar grupos
            admin_group, created = Group.objects.get_or_create(name="ADMINISTRATORS")
            clients_group, created = Group.objects.get_or_create(name="CLIENTS")
            collabs_group, created = Group.objects.get_or_create(name="COLLABORATORS")

            # Adicionar ao grupo administrativo
            user.groups.add(admin_group)

            self.stdout.write("✅ Groupes configurés")

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Erro nos grupos: {e}"))

    def _create_profile_manually(self, user):
        """Criar perfil manualmente"""
        try:
            from profiles.models import Profile

            profile, created = Profile.objects.get_or_create(user=user)

            if created:
                self.stdout.write("✅ Profil créé")
            else:
                self.stdout.write("✅ Profil existant trouvé")

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Erro no perfil: {e}"))

    def _show_user_info(self, user, email, password):
        """Mostrar informações do usuário"""
        self.stdout.write(f"📧 Email: {email}")
        self.stdout.write(f"👤 Nom: {user.first_name} {user.last_name}")
        self.stdout.write(f"🆔 Username: {user.username}")
        self.stdout.write(f"🔑 Type: {user.get_account_type_display()}")

        # Verificações
        self.stdout.write(f"\n🔍 Vérifications:")
        self.stdout.write(f"   ✅ is_staff: {user.is_staff}")
        self.stdout.write(f"   ✅ is_superuser: {user.is_superuser}")
        self.stdout.write(f"   ✅ is_active: {user.is_active}")
        self.stdout.write(f"   ✅ account_type: {user.account_type}")

        # Grupos
        groups = user.groups.all()
        if groups:
            group_names = [g.name for g in groups]
            self.stdout.write(f"   ✅ groupes: {', '.join(group_names)}")

        # Perfil
        if hasattr(user, "profile"):
            self.stdout.write(f"   ✅ profil: Créé")
        else:
            self.stdout.write(f"   ⚠️  profil: Non trouvé")

        # Teste de autenticação
        self.stdout.write(f"\n🧪 Test d'authentification:")
        from django.contrib.auth import authenticate

        test_user = authenticate(username=email, password=password)
        if test_user:
            self.stdout.write(f"   ✅ Authentification réussie!")
        else:
            self.stdout.write(f"   ❌ Échec de l'authentification")

        self.stdout.write(self.style.HTTP_INFO(f"\n🌐 Connexion: /admin/ avec {email}"))

    def _get_email(self, options):
        """Obter email do superuser"""
        email = options.get("email")
        while not email:
            if options.get("no_input"):
                self.stdout.write(self.style.ERROR("Email requis en mode --no-input"))
                sys.exit(1)
            email = input("📧 Email du super administrateur: ").strip()
            if not email:
                self.stdout.write(self.style.ERROR("L'email est obligatoire."))
                continue
            if User.objects.filter(email__iexact=email).exists():
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Un utilisateur avec l\'email "{email}" existe déjà.'
                    )
                )
                email = None
                continue
            if "@" not in email or "." not in email:
                self.stdout.write(self.style.ERROR("Format d'email invalide."))
                email = None
                continue
        return email.lower()

    def _get_first_name(self, options):
        """Obter primeiro nome"""
        first_name = options.get("first_name")
        while not first_name:
            if options.get("no_input"):
                return "Super"
            first_name = input("👤 Prénom: ").strip()
            if not first_name:
                self.stdout.write(self.style.ERROR("Le prénom est obligatoire."))
                continue
            if len(first_name) < 2:
                self.stdout.write(
                    self.style.ERROR("Le prénom doit contenir au moins 2 caractères.")
                )
                first_name = None
                continue
        return first_name.strip().title()

    def _get_last_name(self, options):
        """Obter sobrenome"""
        last_name = options.get("last_name")
        while not last_name:
            if options.get("no_input"):
                return "Admin"
            last_name = input("👤 Nom: ").strip()
            if not last_name:
                self.stdout.write(self.style.ERROR("Le nom est obligatoire."))
                continue
            if len(last_name) < 2:
                self.stdout.write(
                    self.style.ERROR("Le nom doit contenir au moins 2 caractères.")
                )
                last_name = None
                continue
        return last_name.strip().title()

    def _get_password(self, options):
        """Obter senha"""
        if options.get("no_input"):
            return "admin123"
        while True:
            password = getpass.getpass("🔑 Mot de passe: ")
            if len(password) < 8:
                self.stdout.write(
                    self.style.ERROR(
                        "Le mot de passe doit contenir au moins 8 caractères."
                    )
                )
                continue
            password2 = getpass.getpass("🔑 Confirmez le mot de passe: ")
            if password != password2:
                self.stdout.write(
                    self.style.ERROR("Les mots de passe ne correspondent pas.")
                )
                continue
            return password
