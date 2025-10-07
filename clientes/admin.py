from django.contrib import admin
from .models import Cliente, AdresseLivraison, AdresseTransporteur, AdresseChantier, TarifTVAClient


class AdresseLivraisonInline(admin.TabularInline):
    model = AdresseLivraison
    extra = 1
    fields = ['nom', 'copier_adresse_principale', 'adresse', 'code_postal', 'ville', 'pays']


class AdresseTransporteurInline(admin.TabularInline):
    model = AdresseTransporteur
    extra = 1
    fields = ['nom', 'copier_adresse_principale', 'adresse', 'code_postal', 'ville', 'pays']


class AdresseChantiersInline(admin.TabularInline):
    model = AdresseChantier
    extra = 1
    fields = ['nom', 'adresse', 'code_postal', 'ville', 'pays', 'responsable_nom']


class TarifTVAClientInline(admin.TabularInline):
    model = TarifTVAClient
    extra = 1
    fields = ['description', 'taux_tva', 'actif']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom_complet', 'email', 'telephone', 'status', 'date_creation']
    list_filter = ['status', 'date_creation', 'pays']
    search_fields = ['code', 'nom', 'prenom', 'raison_sociale', 'email']
    readonly_fields = ['date_creation', 'date_modification']

    fieldsets = (
        ('Informations principales', {
            'fields': ('code', 'civilite', 'raison_sociale', 'nom', 'prenom', 'status')
        }),
        ('Adresse', {
            'fields': ('adresse', 'code_postal', 'ville', 'pays')
        }),
        ('Contact', {
            'fields': ('telephone', 'mobile', 'email', 'url')
        }),
        ('Informations entreprise', {
            'fields': ('activite', 'siret', 'code_ape', 'tva_intra'),
            'classes': ('collapse',)
        }),
        ('Conditions commerciales', {
            'fields': ('taux_tva_defaut', 'remise_globale', 'conditions_paiement')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    inlines = [AdresseLivraisonInline, AdresseTransporteurInline, AdresseChantiersInline, TarifTVAClientInline]


@admin.register(AdresseLivraison)
class AdresseLivraisonAdmin(admin.ModelAdmin):
    list_display = ['client', 'nom', 'ville', 'pays']
    list_filter = ['pays']
    search_fields = ['client__nom', 'client__raison_sociale', 'nom', 'ville']


@admin.register(AdresseTransporteur)
class AdresseTransporteurAdmin(admin.ModelAdmin):
    list_display = ['client', 'nom', 'ville', 'pays']
    list_filter = ['pays']
    search_fields = ['client__nom', 'client__raison_sociale', 'nom', 'ville']


@admin.register(AdresseChantier)
class AdresseChantiersAdmin(admin.ModelAdmin):
    list_display = ['client', 'nom', 'ville', 'date_creation']
    list_filter = ['pays', 'date_creation']
    search_fields = ['client__nom', 'client__raison_sociale', 'nom', 'ville']


@admin.register(TarifTVAClient)
class TarifTVAClientAdmin(admin.ModelAdmin):
    list_display = ['client', 'description', 'taux_tva', 'actif']
    list_filter = ['actif', 'taux_tva']
    search_fields = ['client__nom', 'client__raison_sociale', 'description']
