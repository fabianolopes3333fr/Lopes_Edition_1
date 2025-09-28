from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin personalizado para Profile"""

    # Configurações de exibição
    list_display = [
        "user_info_display",
        "avatar_display",
        "contact_info_display",
        "location_display",
        "preferences_display",
        "completion_status",
        "updated_display",
    ]
    list_filter = [
        "user__account_type",
        "receive_notifications",
        "receive_newsletters",
        "country",
        "updated_at",
        "created_at",
    ]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone",
        "city",
        "display_username",
    ]
    ordering = ["-updated_at"]

    # Configurações de formulário
    fieldsets = (
        ("👤 Utilisateur", {"fields": ("user", "display_username")}),
        ("📸 Photo de profil", {"fields": ("avatar",)}),
        ("📞 Contact", {"fields": ("phone",), "classes": ["wide"]}),
        (
            "📍 Adresse",
            {
                "fields": ("address", "city", "postal_code", "country"),
                "classes": ["wide"],
            },
        ),
        (
            "⚙️ Préférences",
            {
                "fields": ("receive_notifications", "receive_newsletters"),
                "classes": ["collapse"],
            },
        ),
        (
            "📅 Informations système",
            {"fields": ("created_at", "updated_at"), "classes": ["collapse"]},
        ),
    )

    readonly_fields = ["created_at", "updated_at", "display_username"]

    # Configurações de paginação
    list_per_page = 20

    def get_queryset(self, request):
        """Otimizar consultas"""
        qs = super().get_queryset(request)
        return qs.select_related("user")

    def user_info_display(self, obj):
        """Informações do usuário"""
        user_url = reverse("admin:accounts_user_change", args=[obj.user.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            "<strong>{}</strong><br>"
            '<small style="color: #666;">{}</small><br>'
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px;">{}</span>'
            "</a>",
            user_url,
            obj.user.get_full_name(),
            obj.user.email,
            self._get_account_type_color(obj.user.account_type),
            obj.user.get_account_type_display(),
        )

    user_info_display.short_description = "👤 Utilisateur"
    user_info_display.admin_order_field = "user__first_name"

    def avatar_display(self, obj):
        """Exibir avatar"""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; '
                'border-radius: 50%; object-fit: cover; border: 2px solid #E5E7EB;" />',
                obj.avatar.url,
            )
        else:
            # Avatar padrão com iniciais
            initials = (
                f"{obj.user.first_name[0]}{obj.user.last_name[0]}"
                if obj.user.first_name and obj.user.last_name
                else "?"
            )
            return format_html(
                '<div style="width: 50px; height: 50px; border-radius: 50%; '
                "background: linear-gradient(135deg, #3B82F6, #8B5CF6); "
                "display: flex; align-items: center; justify-content: center; "
                'color: white; font-weight: bold; font-size: 18px;">{}</div>',
                initials,
            )

    avatar_display.short_description = "📸 Avatar"

    def contact_info_display(self, obj):
        """Informações de contato"""
        phone_icon = "📞" if obj.phone else "📞❌"
        phone_text = obj.phone if obj.phone else "Non renseigné"

        return format_html(
            '<div style="font-size: 12px;">' "{} {}<br>" "📧 {}" "</div>",
            phone_icon,
            phone_text,
            obj.user.email,
        )

    contact_info_display.short_description = "📞 Contact"

    def location_display(self, obj):
        """Informações de localização"""
        location_parts = []

        if obj.city:
            location_parts.append(obj.city)
        if obj.postal_code:
            location_parts.append(obj.postal_code)
        if obj.country:
            location_parts.append(obj.country)

        if location_parts:
            location = ", ".join(location_parts)
            return format_html(
                '<div style="font-size: 12px;">' "📍 {}" "</div>", location
            )
        return format_html('<em style="color: #9CA3AF;">Non renseigné</em>')

    location_display.short_description = "📍 Localisation"

    def preferences_display(self, obj):
        """Preferências do usuário"""
        notifications = "🔔" if obj.receive_notifications else "🔕"
        newsletter = "📰" if obj.receive_newsletters else "📰❌"

        return format_html(
            '<div style="font-size: 12px;">'
            "{} Notifications<br>"
            "{} Newsletter"
            "</div>",
            notifications,
            newsletter,
        )

    preferences_display.short_description = "⚙️ Préférences"

    def completion_status(self, obj):
        """Status de completude do perfil"""
        required_fields = [obj.phone, obj.address, obj.city]
        completed = sum(1 for field in required_fields if field and field.strip())
        total = len(required_fields)
        percentage = int((completed / total) * 100)

        # Cor baseada na completude
        if percentage >= 80:
            color = "#10B981"  # Verde
            icon = "✅"
        elif percentage >= 50:
            color = "#F59E0B"  # Amarelo
            icon = "⚠️"
        else:
            color = "#EF4444"  # Vermelho
            icon = "❌"

        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<div style="width: 60px; height: 8px; background-color: #E5E7EB; border-radius: 4px;">'
            '<div style="width: {}%; height: 100%; background-color: {}; border-radius: 4px;"></div>'
            "</div>"
            '<span style="font-size: 12px; font-weight: bold; color: {};">{} {}%</span>'
            "</div>",
            percentage,
            color,
            color,
            icon,
            percentage,
        )

    completion_status.short_description = "📊 Complétude"

    def updated_display(self, obj):
        """Data de última atualização"""
        return format_html(
            '<span style="font-size: 12px;">{}<br>'
            '<small style="color: #9CA3AF;">{}</small></span>',
            obj.updated_at.strftime("%d/%m/%Y"),
            obj.updated_at.strftime("%H:%M"),
        )

    updated_display.short_description = "🕒 Mis à jour"
    updated_display.admin_order_field = "updated_at"

    def _get_account_type_color(self, account_type):
        """Retorna cor para o tipo de conta"""
        colors = {
            "CLIENT": "#10B981",  # Verde
            "COLLABORATOR": "#3B82F6",  # Azul
            "ADMINISTRATOR": "#8B5CF6",  # Roxo
        }
        return colors.get(account_type, "#6B7280")

    def save_model(self, request, obj, form, change):
        """Override para logging personalizado"""
        super().save_model(request, obj, form, change)

        if not change:
            self.message_user(
                request,
                format_html(
                    "Perfil criado para <strong>{}</strong>!", obj.user.get_full_name()
                ),
            )
        else:
            self.message_user(
                request,
                format_html(
                    "Perfil de <strong>{}</strong> atualizado com sucesso!",
                    obj.user.get_full_name(),
                ),
            )
