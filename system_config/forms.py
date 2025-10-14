from django import forms
from .models import (
    CompanySettings,
    Civilite,
    LegalForm,
    PaymentMode,
    TaxRate,
    PaymentCondition,
    AutoEntrepreneurParameters,
    InterfaceSettings,
    EmailSettings,
)


# ===================== CLASSES CSS PADRÃO =====================
INPUT_CLASSES = 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
SELECT_CLASSES = 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
TEXTAREA_CLASSES = 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y'
CHECKBOX_CLASSES = 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
FILE_CLASSES = 'block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer'


# ===================== FORMS SINGLETON =====================
class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        exclude = ("updated_at",)
        widgets = {
            'raison_sociale': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'adresse': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Adresse'}),
            'code_postal': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Code Postal'}),
            'ville': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Ville'}),
            'pays': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'siret': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'code_ape': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'code_rcs': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'tva_intra': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'tel': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'mobile': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'fax': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASSES}),
            'site_internet': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'activite': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'forme_juridique': forms.Select(attrs={'class': SELECT_CLASSES}),
            'type_entreprise': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'capital': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'responsable_civilite': forms.Select(attrs={'class': SELECT_CLASSES}),
            'responsable_nom': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'responsable_prenom': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_raison_sociale': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_adresse': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_code_postal': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_ville': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_nom_prenom': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_tel': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_mobile': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_fax': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'expert_email': forms.EmailInput(attrs={'class': INPUT_CLASSES}),
        }


class AutoEntrepreneurParametersForm(forms.ModelForm):
    class Meta:
        model = AutoEntrepreneurParameters
        exclude = ("updated_at",)
        widgets = {
            'default_product_type': forms.Select(attrs={'class': SELECT_CLASSES}),
            'declaration_periodicite': forms.Select(attrs={'class': SELECT_CLASSES}),
            'biens_taux_cotisation_sociale': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'biens_taux_imposition': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'biens_taux_formation_pro': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'biens_taux_chambre_consulaire': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'services_taux_cotisation_sociale': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'services_taux_imposition': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'services_taux_formation_pro': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'services_taux_chambre_consulaire': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        }


class InterfaceSettingsForm(forms.ModelForm):
    class Meta:
        model = InterfaceSettings
        fields = ("logo", "background_image")
        widgets = {
            'logo': forms.FileInput(attrs={'class': FILE_CLASSES}),
            'background_image': forms.FileInput(attrs={'class': FILE_CLASSES}),
        }


class EmailSettingsForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES, 'render_value': True}),
        required=False
    )

    class Meta:
        model = EmailSettings
        exclude = ("updated_at",)
        widgets = {
            'host': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'port': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'username': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'use_tls': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'use_ssl': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'actif': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }


# ===================== FORMS LISTAS =====================
class CiviliteForm(forms.ModelForm):
    class Meta:
        model = Civilite
        fields = ["label", "abreviation", "actif"]
        widgets = {
            'label': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'abreviation': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'actif': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }


class LegalFormForm(forms.ModelForm):
    class Meta:
        model = LegalForm
        fields = ["name", "description", "actif"]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3}),
            'actif': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }


class PaymentModeForm(forms.ModelForm):
    class Meta:
        model = PaymentMode
        fields = ["name", "ordre", "actif"]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'ordre': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'actif': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }


class TaxRateForm(forms.ModelForm):
    class Meta:
        model = TaxRate
        fields = ["name", "rate", "tax_type", "actif"]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'rate': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'step': '0.01'}),
            'tax_type': forms.Select(attrs={'class': SELECT_CLASSES}),
            'actif': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }


class PaymentConditionForm(forms.ModelForm):
    class Meta:
        model = PaymentCondition
        fields = ["code", "description", "actif"]
        widgets = {
            'code': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'actif': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        }
