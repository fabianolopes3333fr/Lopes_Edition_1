from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from .models import User
#from profiles.models import Profile

# Unregister the default Group admin
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizado para o modelo User"""

    # Configurações de exibição
    list_display = [
        "email",
        "full_name_display",
        "account_type_badge",
        "is_active_badge",
        "groups_display",
        "date_joined_display",
        "actions_display",
    ]
    list_filter = [
        "account_type",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
        "groups",
    ]
    search_fields = ["email", "first_name", "last_name", "username"]
    ordering = ["-date_joined"]

    # Configurações de formulário
    fieldsets = (
        ("🔐 Informations de connexion", {"fields": ("email", "password")}),
        (
            "👤 Informations personnelles",
            {"fields": ("first_name", "last_name", "account_type")},
        ),
        (
            "🔑 Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "📅 Dates importantes",
            {"fields": ("last_login", "date_joined"), "classes": ["collapse"]},
        ),
    )

    add_fieldsets = (
        (
            "🆕 Créer un nouvel utilisateur",
            {
                "classes": ["wide"],
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "account_type",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    readonly_fields = ["date_joined", "last_login"]
    filter_horizontal = ["groups", "user_permissions"]

    # Configurações de paginação
    list_per_page = 25
    list_max_show_all = 100

    def get_queryset(self, request):
        """Otimizar consultas com select_related e prefetch_related"""
        qs = super().get_queryset(request)
        return qs.select_related("profile").prefetch_related("groups")

    def full_name_display(self, obj):
        """Exibir nome completo com link para perfil"""
        full_name = obj.get_full_name()
        if hasattr(obj, "profile") and obj.profile:
            profile_url = reverse(
                "admin:profiles_profile_change", args=[obj.profile.pk]
            )
            return format_html(
                '<a href="{}" style="text-decoration: none;">'
                "<strong>{}</strong><br>"
                '<small style="color: #666;">@{}</small>'
                "</a>",
                profile_url,
                full_name,
                obj.username,
            )
        return format_html(
            '<strong>{}</strong><br><small style="color: #999;">Sem perfil</small>',
            full_name,
        )

    full_name_display.short_description = "👤 Nome"
    full_name_display.admin_order_field = "first_name"

    def account_type_badge(self, obj):
        """Badge colorido para tipo de conta"""
        colors = {
            "CLIENT": "#10B981",  # Verde
            "COLLABORATOR": "#3B82F6",  # Azul
            "ADMINISTRATOR": "#8B5CF6",  # Roxo
        }
        color = colors.get(obj.account_type, "#6B7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_account_type_display(),
        )

    account_type_badge.short_description = "🏷️ Type"
    account_type_badge.admin_order_field = "account_type"

    def is_active_badge(self, obj):
        """Badge para status ativo/inativo"""
        if obj.is_active:
            return format_html(
                '<span style="color: #10B981; font-weight: bold;">● Actif</span>'
            )
        return format_html(
            '<span style="color: #EF4444; font-weight: bold;">● Inactif</span>'
        )

    is_active_badge.short_description = "🟢 Statut"
    is_active_badge.admin_order_field = "is_active"

    def groups_display(self, obj):
        """Exibir grupos do usuário"""
        groups = obj.groups.all()
        if not groups:
            return format_html('<em style="color: #9CA3AF;">Aucun groupe</em>')

        badges = []
        for group in groups:
            badges.append(
                f'<span style="background-color: #F3F4F6; color: #374151; '
                f'padding: 2px 6px; border-radius: 8px; font-size: 10px;">{group.name}</span>'
            )
        return format_html(" ".join(badges))

    groups_display.short_description = "👥 Groupes"

    def date_joined_display(self, obj):
        """Data de cadastro formatada"""
        return format_html(
            '<span style="font-size: 12px;">{}<br>'
            '<small style="color: #9CA3AF;">{}</small></span>',
            obj.date_joined.strftime("%d/%m/%Y"),
            obj.date_joined.strftime("%H:%M"),
        )

    date_joined_display.short_description = "📅 Cadastro"
    date_joined_display.admin_order_field = "date_joined"

    def actions_display(self, obj):
        """Ações rápidas"""
        actions = []

        # Link para perfil
        if hasattr(obj, "profile"):
            profile_url = reverse(
                "admin:profiles_profile_change", args=[obj.profile.pk]
            )
            actions.append(f'<a href="{profile_url}" title="Ver perfil">👤</a>')

        # Toggle ativo/inativo
        if obj.is_active:
            actions.append('<span title="Usuário ativo">🟢</span>')
        else:
            actions.append('<span title="Usuário inativo">🔴</span>')

        # Admin badge
        if obj.is_staff:
            actions.append('<span title="Staff">⚙️</span>')

        return format_html(" ".join(actions))

    actions_display.short_description = "⚡ Ações"

    def save_model(self, request, obj, form, change):
        """Override para logging personalizado"""
        if not change:  # Novo usuário
            obj.save()
            self.message_user(
                request,
                format_html(
                    "Usuário <strong>{}</strong> criado com sucesso! "
                    "Tipo: <strong>{}</strong>",
                    obj.email,
                    obj.get_account_type_display(),
                ),
            )
        else:
            obj.save()
            self.message_user(
                request,
                format_html(
                    "Usuário <strong>{}</strong> atualizado com sucesso!", obj.email
                ),
            )


# Customizar o admin site
admin.site.site_header = "🎨 LOPES PEINTURE - Administration"
admin.site.site_title = "LOPES PEINTURE Admin"
admin.site.index_title = "Tableau de bord administratif"
