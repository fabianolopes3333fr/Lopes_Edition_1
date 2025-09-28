from django.contrib import admin
from .models import Projeto, ImageProjeto


class ImageProjetoInline(admin.TabularInline):
    model = ImageProjeto
    extra = 3
    fields = ("image", "legende", "ordre")


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = (
        "titre",
        "ville",
        "type_projet",
        "status",
        "date_debut",
        "visible_site",
    )
    list_filter = ("status", "type_projet", "ville", "visible_site")
    search_fields = ("titre", "ville", "description")
    list_editable = ("status", "visible_site")
    date_hierarchy = "date_creation"
    inlines = [ImageProjetoInline]

    fieldsets = (
        ("Informations générales", {"fields": ("titre", "description", "type_projet")}),
        ("Localisation", {"fields": ("ville", "adresse")}),
        (
            "Projet",
            {
                "fields": (
                    "status",
                    "date_debut",
                    "date_fin",
                    "surface_m2",
                    "prix_estime",
                )
            },
        ),
        ("Média", {"fields": ("image_principale", "visible_site")}),
    )
