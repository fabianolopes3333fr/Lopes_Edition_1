from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.db.models import Sum, Avg, Count
from profiles.models import Profile
from projetos.models import Projeto

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

        # Estatísticas de projetos
        total_projetos = Projeto.objects.count()
        projetos_novos = Projeto.objects.filter(status="nouveau").count()
        projetos_em_curso = Projeto.objects.filter(status="en_cours").count()
        projetos_terminados = Projeto.objects.filter(status="termine").count()
        projetos_suspensos = Projeto.objects.filter(status="suspendu").count()
        projetos_visiveis = Projeto.objects.filter(visible_site=True).count()

        # Projetos recentes (últimos 30 dias)
        projetos_recentes = Projeto.objects.filter(
            date_creation__gte=timezone.now() - timedelta(days=30)
        ).count()

        # Estatísticas financeiras dos projetos
        valor_total_estimado = Projeto.objects.aggregate(
            total=Sum("prix_estime")
        )["total"] or 0

        valor_medio_projetos = Projeto.objects.aggregate(
            media=Avg("prix_estime")
        )["media"] or 0

        # Estatísticas por tipo de projeto
        tipos_projetos = Projeto.objects.values("type_projet").annotate(
            count=Count("id")
        ).order_by("-count")

        # Estatísticas por cidade (top 5)
        cidades_projetos = Projeto.objects.values("ville").annotate(
            count=Count("id")
        ).order_by("-count")[:5]

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
                    "total_projetos": total_projetos,
                    "projetos_novos": projetos_novos,
                    "projetos_em_curso": projetos_em_curso,
                    "projetos_terminados": projetos_terminados,
                    "projetos_suspensos": projetos_suspensos,
                    "projetos_visiveis": projetos_visiveis,
                    "projetos_recentes": projetos_recentes,
                    "valor_total_estimado": valor_total_estimado,
                    "valor_medio_projetos": valor_medio_projetos,
                    "tipos_projetos": tipos_projetos,
                    "cidades_projetos": cidades_projetos,
                }
            }
        )

        return super().index(request, extra_context)


# Instância personalizada do admin
admin_site = LopesPeintureAdminSite(name="lopes_admin")
