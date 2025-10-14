from django.contrib import admin
from .models import (
    Civilite, LegalForm, PaymentMode, PaymentCondition, TaxRate,
    CompanySettings, AutoEntrepreneurParameters, InterfaceSettings, EmailSettings
)

@admin.register(Civilite)
class CiviliteAdmin(admin.ModelAdmin):
    list_display = ("label", "abreviation", "actif")
    list_filter = ("actif",)
    search_fields = ("label", "abreviation")

@admin.register(LegalForm)
class LegalFormAdmin(admin.ModelAdmin):
    list_display = ("name", "actif")
    list_filter = ("actif",)
    search_fields = ("name",)

@admin.register(PaymentMode)
class PaymentModeAdmin(admin.ModelAdmin):
    list_display = ("ordre", "name", "actif")
    ordering = ("ordre", "name")
    list_filter = ("actif",)
    search_fields = ("name",)

@admin.register(PaymentCondition)
class PaymentConditionAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "actif")
    list_filter = ("actif",)
    search_fields = ("code", "description")

@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ("name", "rate", "tax_type", "actif")
    list_filter = ("tax_type", "actif")
    search_fields = ("name",)

@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ("raison_sociale", "ville", "pays", "siret", "updated_at")

@admin.register(AutoEntrepreneurParameters)
class AutoEntrepreneurParametersAdmin(admin.ModelAdmin):
    list_display = ("default_product_type", "declaration_periodicite", "updated_at")

@admin.register(InterfaceSettings)
class InterfaceSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "logo", "background_image", "updated_at")

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ("host", "port", "username", "from_email", "actif", "updated_at")
    list_filter = ("actif",)

