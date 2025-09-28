from django.contrib import admin
from .models import Contato, PieceJointe


class PieceJointeInline(admin.TabularInline):
    model = PieceJointe
    extra = 0
    readonly_fields = ["nom_original", "taille", "date_upload"]


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "prenom",
        "email",
        "type_contact",
        "sujet",
        "status",
        "date_creation",
    ]
    list_filter = ["type_contact", "status", "date_creation", "ville_projet"]
    search_fields = ["nom", "prenom", "email", "sujet", "message"]
    list_editable = ["status"]
    readonly_fields = ["date_creation", "ip_address", "user_agent"]
    date_hierarchy = "date_creation"
    inlines = [PieceJointeInline]

    fieldsets = (
        (
            "Informations personnelles",
            {"fields": ("nom", "prenom", "email", "telephone")},
        ),
        ("Demande", {"fields": ("type_contact", "sujet", "message")}),
        (
            "Informations du projet",
            {
                "fields": (
                    "adresse_projet",
                    "ville_projet",
                    "surface_estimee",
                    "budget_estime",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Gestion", {"fields": ("status", "notes_internes", "date_traitement")}),
        (
            "Métadonnées",
            {
                "fields": ("date_creation", "ip_address", "user_agent"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["marquer_comme_traite", "marquer_comme_en_cours"]

    def marquer_comme_traite(self, request, queryset):
        updated = queryset.update(status="traite", date_traitement=timezone.now())
        self.message_user(request, f"{updated} contatos marcados como tratados.")

    marquer_comme_traite.short_description = "Marquer comme traité"

    def marquer_comme_en_cours(self, request, queryset):
        updated = queryset.update(status="en_cours")
        self.message_user(request, f"{updated} contatos marcados como em curso.")

    marquer_comme_en_cours.short_description = "Marquer comme en cours"


@admin.register(PieceJointe)
class PieceJointeAdmin(admin.ModelAdmin):
    list_display = ["nom_original", "contato", "taille", "date_upload"]
    list_filter = ["date_upload"]
    search_fields = ["nom_original", "contato__nom", "contato__prenom"]
    readonly_fields = ["taille", "date_upload"]
