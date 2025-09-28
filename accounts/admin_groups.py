from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin personalizado para Groups"""

    list_display = [
        "name_display",
        "users_count",
        "permissions_count",
        "description_display",
    ]
    search_fields = ["name"]
    filter_horizontal = ["permissions"]

    fieldsets = (
        ("📋 Informations du groupe", {"fields": ("name",)}),
        ("🔑 Permissions", {"fields": ("permissions",), "classes": ["wide"]}),
    )

    def get_queryset(self, request):
        """Otimizar consultas"""
        qs = super().get_queryset(request)
        return qs.prefetch_related("user_set", "permissions")

    def name_display(self, obj):
        """Nome do grupo com ícone"""
        icons = {
            "CLIENTS": "👥",
            "COLLABORATORS": "🤝",
            "ADMINISTRATORS": "👑",
        }
        icon = icons.get(obj.name, "🏷️")

        return format_html(
            '<span style="font-size: 16px;">{} <strong>{}</strong></span>',
            icon,
            obj.name,
        )

    name_display.short_description = "📋 Nom du groupe"
    name_display.admin_order_field = "name"

    def users_count(self, obj):
        """Número de usuários no grupo"""
        count = obj.user_set.count()

        if count == 0:
            color = "#9CA3AF"
        elif count < 5:
            color = "#F59E0B"
        else:
            color = "#10B981"

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{} utilisateur{}</span>',
            color,
            count,
            "s" if count != 1 else "",
        )

    users_count.short_description = "👤 Utilisateurs"

    def permissions_count(self, obj):
        """Número de permissões do grupo"""
        count = obj.permissions.count()
        total_permissions = Permission.objects.count()
        percentage = (
            int((count / total_permissions) * 100) if total_permissions > 0 else 0
        )

        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<span style="font-size: 12px; font-weight: bold;">{} permissions</span>'
            '<div style="width: 60px; height: 6px; background-color: #E5E7EB; border-radius: 3px;">'
            '<div style="width: {}%; height: 100%; background-color: #3B82F6; border-radius: 3px;"></div>'
            "</div>"
            '<span style="font-size: 10px; color: #9CA3AF;">{}%</span>'
            "</div>",
            count,
            percentage,
            percentage,
        )

    permissions_count.short_description = "🔑 Permissions"

    def description_display(self, obj):
        """Descrição do grupo"""
        descriptions = {
            "CLIENTS": "Utilisateurs clients avec accès limité aux services",
            "COLLABORATORS": "Employés et partenaires avec accès aux projets",
            "ADMINISTRATORS": "Accès complet à toutes les fonctionnalités",
        }

        description = descriptions.get(obj.name, "Groupe personnalisé")

        return format_html(
            '<em style="color: #6B7280; font-size: 12px;">{}</em>', description
        )

    description_display.short_description = "📝 Description"
