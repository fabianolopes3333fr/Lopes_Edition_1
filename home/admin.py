from django.contrib import admin
from django.utils.html import format_html
from .models import CategoriaColor, Couleur


@admin.register(CategoriaColor)
class CategoriaColorAdmin(admin.ModelAdmin):
    list_display = ["nome", "slug", "icone", "ordem", "ativo", "total_couleurs"]
    list_editable = ["ordem", "ativo"]
    list_filter = ["ativo"]
    search_fields = ["nome", "slug"]
    prepopulated_fields = {"slug": ("nome",)}

    def total_couleurs(self, obj):
        return obj.couleurs.count()

    total_couleurs.short_description = "Total de couleurs"


@admin.register(Couleur)
class CouleurAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "codigo",
        "categoria",
        "preview_couleur",
        "hex_color",
        "disponible",
        "populaire",
    ]
    list_editable = ["disponible", "populaire"]
    list_filter = ["categoria", "disponible", "populaire", "date_creation"]
    search_fields = ["nome", "codigo", "description"]
    readonly_fields = [
        "hex_color",
        "preview_couleur_large",
        "date_creation",
        "date_modification",
    ]

    fieldsets = (
        (
            "Informations générales",
            {"fields": ("nome", "codigo", "categoria", "description")},
        ),
        (
            "Couleur",
            {
                "fields": (
                    "rgb_r",
                    "rgb_g",
                    "rgb_b",
                    "hex_color",
                    "preview_couleur_large",
                )
            },
        ),
        ("Options", {"fields": ("disponible", "populaire")}),
        (
            "Métadonnées",
            {
                "fields": ("date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )

    def preview_couleur(self, obj):
        """Preview pequeno da cor na lista"""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.hex_color,
        )

    preview_couleur.short_description = "Aperçu"

    def preview_couleur_large(self, obj):
        """Preview grande da cor no formulário"""
        return format_html(
            '<div style="width: 100px; height: 50px; background-color: {}; border: 2px solid #ccc; border-radius: 5px; margin: 10px 0;"></div>'
            "<p><strong>RGB:</strong> {}</p>"
            "<p><strong>HEX:</strong> {}</p>",
            obj.hex_color,
            obj.rgb_string,
            obj.hex_color,
        )

    preview_couleur_large.short_description = "Aperçu de la couleur"

    # Ações em massa
    actions = ["marquer_disponible", "marquer_indisponible", "marquer_populaire"]

    def marquer_disponible(self, request, queryset):
        updated = queryset.update(disponible=True)
        self.message_user(request, f"{updated} couleurs marquées comme disponibles.")

    marquer_disponible.short_description = "Marquer comme disponible"

    def marquer_indisponible(self, request, queryset):
        updated = queryset.update(disponible=False)
        self.message_user(request, f"{updated} couleurs marquées comme indisponibles.")

    marquer_indisponible.short_description = "Marquer comme indisponible"

    def marquer_populaire(self, request, queryset):
        updated = queryset.update(populaire=True)
        self.message_user(request, f"{updated} couleurs marquées comme populaires.")

    marquer_populaire.short_description = "Marquer comme populaire"
