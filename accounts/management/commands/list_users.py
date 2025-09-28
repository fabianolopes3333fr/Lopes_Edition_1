from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Listar todos os usuários do sistema"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["client", "collaborateur", "superadmin"],
            help="Filtrar por tipo de usuário",
        )
        parser.add_argument(
            "--active-only",
            action="store_true",
            help="Mostrar apenas usuários ativos",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Liste des Utilisateurs ===\n"))

        # Filtros
        queryset = User.objects.all()

        if options["type"]:
            queryset = queryset.filter(user_type=options["type"])

        if options["active_only"]:
            queryset = queryset.filter(is_active=True)

        # Ordenar por data de criação
        queryset = queryset.order_by("-date_created")

        if not queryset.exists():
            self.stdout.write(self.style.WARNING("Aucun utilisateur trouvé."))
            return

        # Estatísticas
        total = queryset.count()
        clients = queryset.filter(user_type="client").count()
        collaborateurs = queryset.filter(user_type="collaborateur").count()
        superadmins = queryset.filter(user_type="superadmin").count()

        self.stdout.write(f"📊 Total: {total} utilisateurs")
        self.stdout.write(f"👥 Clients: {clients}")
        self.stdout.write(f"🤝 Collaborateurs: {collaborateurs}")
        self.stdout.write(f"⚡ Super Admins: {superadmins}\n")

        # Listar usuários
        for user in queryset:
            status_icon = "✅" if user.is_active else "❌"
            verified_icon = "✅" if user.is_verified else "❌"

            # Obter grupos
            groups = ", ".join([g.name for g in user.groups.all()])

            self.stdout.write(f"{status_icon} {user.email}")
            self.stdout.write(f"   👤 {user.get_full_name()}")
            self.stdout.write(f"   🏷️  Type: {user.get_user_type_display()}")
            self.stdout.write(f'   👥 Groupes: {groups or "Aucun"}')
            self.stdout.write(f"   ✉️  Vérifié: {verified_icon}")
            self.stdout.write(
                f'   📅 Créé: {user.date_created.strftime("%d/%m/%Y %H:%M")}'
            )
            self.stdout.write("")
