from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.html import format_html
from profiles.models import Profile

User = get_user_model()


class LopesPeintureAdminSite(AdminSite):
    """Admin personalizado para LOPES PEINTURE"""

    site_header = "🎨 LOPES PEINTURE - Administration"
    site_title = "LOPES PEINTURE Admin"
    index_title = "Tableau de bord administratif"

    def index(self, request, extra_context=None):
        """Dashboard personalizado"""

        # Estatísticas de usuários
        total_users = User.objects.count()
        clients = User.objects.filter(account_type="CLIENT").count()
        collaborators = User.objects.filter(account_type="COLLABORATOR").count()
        administrators = User.objects.filter(account_type="ADMINISTRATOR").count()
        active_users = User.objects.filter(is_active=True).count()

        # Estatísticas de perfis
        total_profiles = Profile.objects.count()
        complete_profiles = (
            Profile.objects.filter(
                phone__isnull=False, address__isnull=False, city__isnull=False
            )
            .exclude(phone="", address="", city="")
            .count()
        )

        # Usuários recentes (últimos 7 dias)
        from django.utils import timezone
        from datetime import timedelta

        recent_users = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()

        # Estatísticas de grupos
        groups_stats = []
        for group in Group.objects.all():
            groups_stats.append(
                {
                    "name": group.name,
                    "users_count": group.user_set.count(),
                    "permissions_count": group.permissions.count(),
                }
            )

        extra_context = extra_context or {}
        extra_context.update(
            {
                "stats": {
                    "total_users": total_users,
                    "clients": clients,
                    "collaborators": collaborators,
                    "administrators": administrators,
                    "active_users": active_users,
                    "total_profiles": total_profiles,
                    "complete_profiles": complete_profiles,
                    "recent_users": recent_users,
                    "groups_stats": groups_stats,
                }
            }
        )

        return super().index(request, extra_context)


# Instância personalizada do admin
admin_site = LopesPeintureAdminSite(name="lopes_admin")
